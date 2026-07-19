"""Shared append-only runner helpers for scalar Feature Sensor experiments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import subprocess
import sys
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402
from strategies.paaf.data_audit import (  # noqa: E402
    DEFAULT_ROLL_WINDOW,
    contract_roll_neighborhood_mask,
)
from strategies.paaf.evaluation.models import (  # noqa: E402
    EvaluationResult,
    MetricDefinition,
    MetricRecord,
    OutcomeDefinition,
    OutcomeRecord,
)
from strategies.paaf.evidence.hashing import (  # noqa: E402
    canonical_json_dumps,
    hash_canonical_json,
    hash_file,
)
from strategies.paaf.evidence.models import (  # noqa: E402
    ArtifactReference,
    EvidenceRecord,
)
from strategies.paaf.evidence.repository import EvidenceRepository  # noqa: E402
from strategies.paaf.evidence.workflow import (  # noqa: E402
    ExperimentContext,
    ExperimentWorkflow,
)
from strategies.paaf.sensors.base import BaseFeatureSensor  # noqa: E402
from strategies.paaf.sensors.models import FeatureResult  # noqa: E402
from tools.tq_paths import symbol_dir  # noqa: E402


CST = ZoneInfo("Asia/Shanghai")
PERIOD_START = datetime(2024, 1, 1, tzinfo=CST)
PERIOD_END = datetime(2025, 12, 31, 23, 59, 59, tzinfo=CST)
WARMUP_START = datetime(2023, 12, 1, tzinfo=CST)
N_BARS = 60
SAMPLE_INTERVAL = 60


@dataclass(frozen=True)
class ScalarExperimentConfig:
    experiment_id: str
    run_id: str
    sensor_id: str
    sensor_version: str
    artifact_id: str
    evaluation_id: str
    evidence_id: str
    outcome_id: str
    metric_full_id: str
    metric_ex_roll_id: str
    feature_key: str
    input_key: str
    frame_column: str
    lookback: int
    parameters: dict[str, int]
    hypothesis: str


def _git_revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _file_entry(path: Path, *, relative_to: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "relative_path": path.relative_to(relative_to).as_posix(),
        "size": int(stat.st_size),
        "hash": hash_file(path),
        "modified_time": datetime.fromtimestamp(
            stat.st_mtime,
            tz=timezone.utc,
        ).isoformat(),
    }


def _dataset_fingerprint(
    data_dir: Path,
    used_yymms: set[str],
    roll_rule: str,
) -> tuple[str, dict[str, object]]:
    files: list[Path] = [
        data_dir / "rollover_map.parquet",
        data_dir / "manifest.json",
    ]
    for optional in (
        data_dir / "dominant_windows.json",
        data_dir / "rollover_cost_detail.parquet",
    ):
        if optional.is_file():
            files.append(optional)
    for yymm in sorted(used_yymms):
        monthly = data_dir / f"rb_{yymm}.parquet"
        if not monthly.is_file():
            raise FileNotFoundError(monthly)
        files.append(monthly)

    file_manifest = [
        _file_entry(path, relative_to=ROOT)
        for path in files
    ]
    payload = {
        "source_id": "tqsdk_offline / rb / 1m / CbC",
        "file_manifest": file_manifest,
        "file_hashes": {
            str(item["relative_path"]): item["hash"]
            for item in file_manifest
        },
        "construction_metadata": {
            "continuous_contract": "CbC",
            "adjustment": "unadjusted",
            "bar": "1m",
            "roll_rule": roll_rule,
            "data_spec": "docs/07_DATA_SPEC.md@1.0.0",
            "period_start": PERIOD_START.date().isoformat(),
            "period_end": PERIOD_END.date().isoformat(),
        },
    }
    return hash_canonical_json(payload), payload


def _environment_fingerprint() -> str:
    return hash_canonical_json({
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
    })


def _aware_timestamp(value: pd.Timestamp) -> datetime:
    timestamp = value.to_pydatetime()
    return timestamp.replace(tzinfo=CST) if timestamp.tzinfo is None else timestamp


def _experiment_root(config: ScalarExperimentConfig) -> Path:
    return ROOT / "research" / "output" / "evidence" / config.experiment_id


def _frame_values(frame: pd.DataFrame, column: str) -> np.ndarray:
    if column != "open_interest":
        if column not in frame:
            raise KeyError(f"数据缺字段: {column}")
        return frame[column].to_numpy(dtype=float)

    if "open_oi" not in frame:
        raise KeyError("数据缺字段: open_oi")
    if "close_oi" in frame:
        values = frame["close_oi"].where(
            frame["close_oi"].notna(),
            frame["open_oi"],
        )
    else:
        values = frame["open_oi"]
    return values.fillna(0.0).to_numpy(dtype=float)


def run_artifact(
    config: ScalarExperimentConfig,
    sensor: BaseFeatureSensor,
) -> int:
    root = _experiment_root(config)
    artifact_path = (
        root / "artifacts" / config.artifact_id / "feature_results.jsonl"
    )
    if artifact_path.exists() or (root / "manifest.json").exists():
        raise FileExistsError(
            f"{config.experiment_id} 已存在产物；append-only，禁止覆盖"
        )

    frame = build_stitched_raw_frame("rb")
    frame = frame[
        (frame["dt_cst"] >= pd.Timestamp(WARMUP_START))
        & (frame["dt_cst"] <= pd.Timestamp(PERIOD_END))
    ].reset_index(drop=True)
    if frame.empty:
        raise RuntimeError("加载后无可用 bar")

    period_mask = (
        (frame["dt_cst"] >= pd.Timestamp(PERIOD_START))
        & (frame["dt_cst"] <= pd.Timestamp(PERIOD_END))
    )
    yymms = frame["yymm"].astype(str).tolist()
    roll_mask = contract_roll_neighborhood_mask(
        yymms,
        window=DEFAULT_ROLL_WINDOW,
    )
    values = _frame_values(frame, config.frame_column)

    data_dir = symbol_dir("rb")
    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    methods = sorted(
        str(value)
        for value in rollover_map["method"].dropna().unique().tolist()
    )
    roll_rule = methods[0] if len(methods) == 1 else ",".join(methods)
    used_yymms = set(yymms)
    data_fingerprint, dataset_payload = _dataset_fingerprint(
        data_dir,
        used_yymms,
        roll_rule,
    )

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    ready = 0
    null = 0
    roll_neighborhood_n = 0
    with artifact_path.open("x", encoding="utf-8", newline="\n") as output:
        for index in range(len(frame)):
            if not bool(period_mask.iloc[index]):
                continue
            start = max(0, index + 1 - config.lookback)
            result = sensor.observe(
                symbol="rb",
                timeframe="1m",
                timestamp=_aware_timestamp(frame["dt_cst"].iloc[index]),
                window={
                    config.input_key: values[start:index + 1].tolist(),
                    "roll_neighborhood": bool(roll_mask[index]),
                },
                parameters=config.parameters,
            )
            if not isinstance(result, FeatureResult):
                raise TypeError("Sensor 必须返回 FeatureResult")
            output.write(f"{canonical_json_dumps(result.to_dict())}\n")
            written += 1
            if result.values[config.feature_key] is None:
                null += 1
            else:
                ready += 1
            if result.diagnostics["roll_neighborhood"] == "true":
                roll_neighborhood_n += 1

    artifact_ref = ArtifactReference(
        artifact_id=config.artifact_id,
        uri=f"artifacts/{config.artifact_id}/feature_results.jsonl",
        content_hash=hash_file(artifact_path),
        artifact_type="feature_results",
    )
    context = ExperimentContext(
        experiment_id=config.experiment_id,
        sensor_id=config.sensor_id,
        sensor_version=config.sensor_version,
        parameters=config.parameters,
        hypothesis=config.hypothesis,
        code_revision=_git_revision(),
        data_fingerprint=data_fingerprint,
        environment_fingerprint=_environment_fingerprint(),
        subject_kind="feature_sensor",
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
    )
    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    manifest = ExperimentWorkflow(repository).build_manifest(
        context,
        artifact_refs=(artifact_ref,),
    )
    ExperimentWorkflow(repository).persist_manifest(manifest)

    metadata = {
        "experiment_id": config.experiment_id,
        "run_id": config.run_id,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "authorization": "Artifact",
        "symbol": "rb",
        "timeframe": "1m",
        "period_start": PERIOD_START.date().isoformat(),
        "period_end": PERIOD_END.date().isoformat(),
        "feature_rows_written": written,
        "ready": ready,
        "null": null,
        "roll_neighborhood_true": roll_neighborhood_n,
        "roll_window": DEFAULT_ROLL_WINDOW,
        "code_revision": context.code_revision,
        "data_fingerprint": data_fingerprint,
        "environment_fingerprint": context.environment_fingerprint,
        "parameter_fingerprint": manifest.parameter_fingerprint,
        "artifact": artifact_ref.to_dict(),
        "dataset_fingerprint_payload": dataset_payload,
    }
    (root / "run_metadata.json").write_text(
        f"{canonical_json_dumps(metadata)}\n",
        encoding="utf-8",
    )
    print(
        f"[ARTIFACT] {config.experiment_id} rows={written} "
        f"ready={ready} null={null} roll={roll_neighborhood_n}"
    )
    print(f"  hash={artifact_ref.content_hash}")
    return 0


def _load_features(path: Path) -> list[FeatureResult]:
    return [
        FeatureResult.from_dict(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _realized_vol(
    closes: np.ndarray,
    index: int,
) -> float | None:
    if index + N_BARS >= len(closes):
        return None
    window = closes[index:index + N_BARS + 1]
    if np.any(window <= 0):
        return None
    return float(np.std(np.diff(np.log(window)), ddof=0))


def _correlation(
    features: np.ndarray,
    outcomes: np.ndarray,
) -> dict[str, float | int]:
    if len(features) < 4:
        raise RuntimeError(f"有效样本过少: n={len(features)}")
    rho = float(spearmanr(features, outcomes).correlation)
    z = np.arctanh(np.clip(rho, -0.999999, 0.999999))
    se = 1.0 / np.sqrt(len(features) - 3.0)
    return {
        "rho": rho,
        "ci95_low": float(np.tanh(z - 1.96 * se)),
        "ci95_high": float(np.tanh(z + 1.96 * se)),
        "sample_n": len(features),
    }


def classify_association(
    *,
    rho_ex_roll: float,
    ci95_low_ex_roll: float,
    ci95_high_ex_roll: float,
    rho_full: float,
) -> str:
    """Apply the pre-registered effect and roll-robustness gates."""

    ci_excludes_zero = ci95_low_ex_roll > 0 or ci95_high_ex_roll < 0
    same_sign = rho_ex_roll * rho_full > 0
    stable = abs(rho_full - rho_ex_roll) <= 0.05
    detected = (
        abs(rho_ex_roll) >= 0.10
        and ci_excludes_zero
        and same_sign
        and stable
    )
    return "association_detected" if detected else "inconclusive"


def run_evaluation(config: ScalarExperimentConfig) -> int:
    root = _experiment_root(config)
    feature_path = (
        root / "artifacts" / config.artifact_id / "feature_results.jsonl"
    )
    if not feature_path.is_file():
        raise FileNotFoundError(feature_path)

    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    for exists, item_id in (
        (repository.evaluation_exists, config.evaluation_id),
        (repository.outcome_definition_exists, config.outcome_id),
        (repository.metric_definition_exists, config.metric_full_id),
        (repository.metric_definition_exists, config.metric_ex_roll_id),
    ):
        if exists(config.experiment_id, item_id):
            raise FileExistsError(f"{item_id} 已存在；append-only")

    features = _load_features(feature_path)
    artifact_hash = hash_file(feature_path)
    manifest = repository.load_manifest(config.experiment_id)
    artifact_ref = next(
        ref
        for ref in manifest.artifact_refs
        if ref.artifact_id == config.artifact_id
    )
    if artifact_ref.content_hash != artifact_hash:
        raise ValueError("Feature artifact hash 与 Manifest 不一致")

    frame = build_stitched_raw_frame("rb")
    frame = frame[
        frame["dt_cst"] >= pd.Timestamp(features[0].timestamp)
    ].reset_index(drop=True)
    closes = frame["close"].to_numpy(dtype=float)
    index_by_timestamp = {
        pd.Timestamp(timestamp).isoformat(): index
        for index, timestamp in enumerate(frame["dt_cst"])
    }

    full_x: list[float] = []
    full_y: list[float] = []
    ex_x: list[float] = []
    ex_y: list[float] = []
    rejected = {"null": 0, "warmup": 0, "incomplete_future": 0}
    for sample_index in range(0, len(features), SAMPLE_INTERVAL):
        result = features[sample_index]
        value = result.values.get(config.feature_key)
        if value is None:
            rejected["null"] += 1
            continue
        if result.diagnostics.get("warmup_state") != "ready":
            rejected["warmup"] += 1
            continue
        frame_index = index_by_timestamp.get(
            pd.Timestamp(result.timestamp).isoformat()
        )
        if frame_index is None:
            rejected["incomplete_future"] += 1
            continue
        realized = _realized_vol(closes, frame_index)
        if realized is None:
            rejected["incomplete_future"] += 1
            continue
        full_x.append(float(value))
        full_y.append(realized)
        if result.diagnostics.get("roll_neighborhood") == "false":
            ex_x.append(float(value))
            ex_y.append(realized)

    full = _correlation(np.asarray(full_x), np.asarray(full_y))
    ex_roll = _correlation(np.asarray(ex_x), np.asarray(ex_y))
    excluded_n = int(full["sample_n"]) - int(ex_roll["sample_n"])

    outcome = OutcomeDefinition(
        outcome_id=config.outcome_id,
        name="future_realized_volatility_60",
        window={
            "bars_forward": N_BARS,
            "bar": "1m",
            "sampling_interval": SAMPLE_INTERVAL,
            "definition": "std(log_return[t+1:t+N])",
        },
        unit="log_return_std",
        description="Non-overlapping future RV_60 for scalar Feature observations.",
    )
    metric_full = MetricDefinition(
        metric_id=config.metric_full_id,
        name=f"spearman_{config.feature_key}_vs_rv60_full",
        formula_id="spearman_rank_corr_v1",
        higher_is_better=None,
        description="Spearman correlation on full sample.",
    )
    metric_ex = MetricDefinition(
        metric_id=config.metric_ex_roll_id,
        name=f"spearman_{config.feature_key}_vs_rv60_ex_roll",
        formula_id="spearman_rank_corr_v1",
        higher_is_better=None,
        description="Primary Spearman correlation excluding roll neighborhoods.",
    )
    outcome_record = OutcomeRecord(
        definition_id=config.outcome_id,
        values={
            "mean_rv_full": float(np.mean(full_y)),
            "mean_rv_ex_roll": float(np.mean(ex_y)),
            "roll_excluded_n": float(excluded_n),
            "roll_excluded_fraction": excluded_n / int(full["sample_n"]),
        },
        sample_n=float(full["sample_n"]),
        artifact_refs=(config.artifact_id,),
    )
    evaluation = EvaluationResult(
        evaluation_id=config.evaluation_id,
        experiment_id=config.experiment_id,
        evidence_id=None,
        hypothesis=config.hypothesis,
        decision="HOLD",
        outcome_refs=(config.outcome_id,),
        metric_refs=(config.metric_ex_roll_id, config.metric_full_id),
        outcomes=(outcome_record,),
        metrics=(
            MetricRecord(
                metric_id=config.metric_ex_roll_id,
                value=float(ex_roll["rho"]),
                sample_n=float(ex_roll["sample_n"]),
            ),
            MetricRecord(
                metric_id=config.metric_full_id,
                value=float(full["rho"]),
                sample_n=float(full["sample_n"]),
            ),
        ),
        created_at=datetime.now(tz=timezone.utc),
        metadata={
            "primary_sample": "ex_roll",
            "sensitivity_sample": "full",
            "roll_window": str(DEFAULT_ROLL_WINDOW),
            "feature_artifact_hash": artifact_hash,
        },
    )
    repository.save_outcome_definition(config.experiment_id, outcome)
    repository.save_metric_definition(config.experiment_id, metric_full)
    repository.save_metric_definition(config.experiment_id, metric_ex)
    repository.save_evaluation(evaluation)

    report = {
        "experiment_id": config.experiment_id,
        "evaluation_id": config.evaluation_id,
        "created_at": evaluation.created_at.isoformat(),
        "feature": config.feature_key,
        "primary": {"sample": "ex_roll", **ex_roll},
        "sensitivity": {"sample": "full", **full},
        "roll": {
            "window": DEFAULT_ROLL_WINDOW,
            "excluded_n": excluded_n,
            "excluded_fraction": excluded_n / int(full["sample_n"]),
        },
        "rejected": rejected,
        "decision": "HOLD",
        "evidence": "NOT CREATED",
    }
    (root / "evaluation_report.json").write_text(
        f"{canonical_json_dumps(report)}\n",
        encoding="utf-8",
    )
    print(
        f"[EVALUATION] {config.experiment_id} "
        f"ex_roll rho={ex_roll['rho']:.6f} n={ex_roll['sample_n']} "
        f"full rho={full['rho']:.6f} n={full['sample_n']}"
    )
    return 0


def run_evidence(config: ScalarExperimentConfig) -> int:
    root = _experiment_root(config)
    report_path = root / "evaluation_report.json"
    if not report_path.is_file():
        raise FileNotFoundError(report_path)
    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    if repository.evidence_exists(config.experiment_id, config.evidence_id):
        raise FileExistsError(f"{config.evidence_id} 已存在；append-only")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    primary = report["primary"]
    sensitivity = report["sensitivity"]
    rho_ex = float(primary["rho"])
    rho_full = float(sensitivity["rho"])
    ci_low = float(primary["ci95_low"])
    ci_high = float(primary["ci95_high"])
    same_sign = rho_ex * rho_full > 0
    stable = abs(rho_full - rho_ex) <= 0.05
    ci_excludes_zero = ci_low > 0 or ci_high < 0
    conclusion = classify_association(
        rho_ex_roll=rho_ex,
        ci95_low_ex_roll=ci_low,
        ci95_high_ex_roll=ci_high,
        rho_full=rho_full,
    )

    manifest = repository.load_manifest(config.experiment_id)
    evaluation = repository.load_evaluation(
        config.experiment_id,
        config.evaluation_id,
    )
    artifact_ref = next(
        ref
        for ref in manifest.artifact_refs
        if ref.artifact_id == config.artifact_id
    )
    created_at = datetime.now(tz=timezone.utc)
    evidence = EvidenceRecord(
        evidence_id=config.evidence_id,
        experiment_id=config.experiment_id,
        subject_kind="feature_sensor",
        subject_id=config.sensor_id,
        subject_version=config.sensor_version,
        hypothesis=config.hypothesis,
        decision="HOLD",
        feature_artifact_uri=artifact_ref.uri,
        artifact_hash=artifact_ref.content_hash,
        created_at=created_at,
        observation={
            "feature": config.feature_key,
            "sensor": f"{config.sensor_id}@{config.sensor_version}",
            "universe": "rb/1m",
            "period": "2024-01-01..2025-12-31",
        },
        outcome={
            "name": "RV_60",
            "definition": "std(log_return[t+1:t+N])",
            "mean_rv_ex_roll": float(
                evaluation.outcomes[0].values["mean_rv_ex_roll"]
            ),
        },
        window={
            "n_bars": N_BARS,
            "sampling_interval": SAMPLE_INTERVAL,
            "roll_window": DEFAULT_ROLL_WINDOW,
            "primary_sample": "ex_roll",
        },
        metrics={
            "spearman_rho_ex_roll": rho_ex,
            "spearman_ci95_low_ex_roll": ci_low,
            "spearman_ci95_high_ex_roll": ci_high,
            "sample_n_ex_roll": float(primary["sample_n"]),
            "spearman_rho_full": rho_full,
            "sample_n_full": float(sensitivity["sample_n"]),
            "rho_abs_delta": abs(rho_full - rho_ex),
        },
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
        metadata={
            "evaluation_id": config.evaluation_id,
            "hypothesis_conclusion": conclusion,
            "governance_decision": "HOLD",
            "effect_gate_abs_rho": "0.10",
            "robustness_gate_abs_delta": "0.05",
            "ci_excludes_zero": str(ci_excludes_zero).lower(),
            "same_sign_full_ex_roll": str(same_sign).lower(),
            "promotion": "none",
            "sensor_status": "EXPERIMENT",
        },
    )
    repository.save_evidence(evidence)
    summary = {
        "evidence_id": config.evidence_id,
        "experiment_id": config.experiment_id,
        "evaluation_id": config.evaluation_id,
        "hypothesis_conclusion": conclusion,
        "governance_decision": "HOLD",
        "primary": primary,
        "sensitivity": sensitivity,
        "promotion": "none",
        "sensor_status": "EXPERIMENT",
        "created_at": created_at.isoformat(),
    }
    (root / "evidence_summary.json").write_text(
        f"{canonical_json_dumps(summary)}\n",
        encoding="utf-8",
    )
    print(
        f"[EVIDENCE] {config.experiment_id} "
        f"conclusion={conclusion} decision=HOLD promotion=none"
    )
    return 0
