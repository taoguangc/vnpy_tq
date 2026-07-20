"""OPP16_EXP001 event-study runner: Artifact / Evaluation / Evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402
from strategies.paaf.data_audit import (  # noqa: E402
    DEFAULT_ROLL_WINDOW,
    contract_roll_neighborhood_mask,
)
from strategies.paaf.detectors.opp16_two_bar_reversal import (  # noqa: E402
    DEFAULT_BODY_RATIO,
    OPP16TwoBarReversalDetector,
)
from strategies.paaf.domain import Context, Direction  # noqa: E402
from strategies.paaf.evaluation.models import (  # noqa: E402
    EvaluationResult,
    MetricDefinition,
    MetricRecord,
    OutcomeDefinition,
    OutcomeRecord,
)
from strategies.paaf.evidence.hashing import (  # noqa: E402
    canonical_json_dumps,
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
from tools.tq_paths import symbol_dir  # noqa: E402


CST = ZoneInfo("Asia/Shanghai")
PERIOD_START = datetime(2024, 1, 1, tzinfo=CST)
PERIOD_END = datetime(2025, 12, 31, 23, 59, 59, tzinfo=CST)
WARMUP_START = datetime(2023, 12, 1, tzinfo=CST)
N_BARS = 60
BODY_RATIO = DEFAULT_BODY_RATIO
MIN_N = 100
MAX_ABS_DELTA_MEAN = 0.0005
BOOTSTRAP_N = 5000
BOOTSTRAP_SEED = 42


@dataclass(frozen=True)
class Opp16ExperimentConfig:
    experiment_id: str = "OPP16_EXP001"
    run_id: str = "OPP16_EXP001_RUN001"
    detector_id: str = "OPP16"
    detector_version: str = "1.0.0"
    artifact_id: str = "OPP16_EXP001_DETECTIONS"
    evaluation_id: str = "EVAL-OPP16-EXP001-001"
    evidence_id: str = "EV-OPP16-EXP001-001"
    outcome_id: str = "OUT-OPP16-EXP001-ALIGNED-SR60"
    metric_full_id: str = "MET-OPP16-EXP001-MEAN-ALIGNED-FULL"
    metric_ex_roll_id: str = "MET-OPP16-EXP001-MEAN-ALIGNED-EX-ROLL"
    hypothesis: str = (
        "OPP16 裸两棒反转事件后 aligned SR_60 存在可检出正边沿（H0：无实质正边沿）"
    )


CONFIG = Opp16ExperimentConfig()


def classify_opp16_association(
    *,
    mean_ex_roll: float,
    ci95_low_ex_roll: float,
    mean_full: float,
    sample_n_ex_roll: int,
) -> str:
    same_sign = mean_ex_roll * mean_full > 0
    stable = abs(mean_full - mean_ex_roll) <= MAX_ABS_DELTA_MEAN
    if (
        sample_n_ex_roll >= MIN_N
        and ci95_low_ex_roll > 0.0
        and mean_ex_roll >= 0.0
        and same_sign
        and stable
    ):
        return "association_detected"
    return "inconclusive"


def _git_revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _environment_fingerprint() -> str:
    return (
        f"python={sys.version.split()[0]};"
        f"platform={platform.platform()};"
        f"numpy={np.__version__};"
        f"pandas={pd.__version__}"
    )


def _experiment_root(config: Opp16ExperimentConfig) -> Path:
    return ROOT / "research" / "output" / "evidence" / config.experiment_id


def _aware_timestamp(value: Any) -> datetime:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize(CST)
    else:
        ts = ts.tz_convert(CST)
    return ts.to_pydatetime()


def _dataset_fingerprint(
    data_dir: Path,
    used_yymms: set[str],
    roll_rule: str,
) -> tuple[str, dict[str, Any]]:
    from strategies.paaf.evidence.hashing import hash_canonical_json, hash_file

    files = [
        data_dir / "manifest.json",
        data_dir / "dominant_windows.json",
        data_dir / "rollover_map.parquet",
    ]
    for yymm in sorted(used_yymms):
        matches = list(data_dir.glob(f"*_{yymm}.parquet"))
        if matches:
            files.append(matches[0])
    file_hashes = {
        path.relative_to(ROOT).as_posix(): hash_file(path)
        for path in files
        if path.is_file()
    }
    payload = {
        "construction_metadata": {
            "adjustment": "unadjusted",
            "bar": "1m->5m",
            "continuous_contract": "CbC",
            "data_spec": "docs/07_DATA_SPEC.md@1.0.0",
            "period_end": PERIOD_END.date().isoformat(),
            "period_start": PERIOD_START.date().isoformat(),
            "roll_rule": roll_rule,
        },
        "file_hashes": file_hashes,
    }
    return hash_canonical_json(payload), payload


def _build_5m_frame(frame_1m: pd.DataFrame) -> pd.DataFrame:
    yymms = frame_1m["yymm"].astype(str).tolist()
    roll_1m = contract_roll_neighborhood_mask(
        yymms,
        window=DEFAULT_ROLL_WINDOW,
    )
    work = frame_1m.copy()
    work["roll_neighborhood"] = roll_1m
    work = work.set_index("dt_cst").sort_index()
    agg = (
        work.resample("5min", label="left", closed="left")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "yymm": "last",
                "roll_neighborhood": "any",
            }
        )
        .dropna(subset=["open", "high", "low", "close"])
    )
    agg["roll_neighborhood"] = agg["roll_neighborhood"].astype(bool)
    return agg.reset_index()


def _ohlc_window(frame: pd.DataFrame, end_index: int) -> SimpleNamespace:
    start = max(0, end_index - 1)
    slice_frame = frame.iloc[start:end_index + 1]
    return SimpleNamespace(
        open=tuple(float(value) for value in slice_frame["open"].tolist()),
        high=tuple(float(value) for value in slice_frame["high"].tolist()),
        low=tuple(float(value) for value in slice_frame["low"].tolist()),
        close=tuple(float(value) for value in slice_frame["close"].tolist()),
        count=len(slice_frame),
        inited=len(slice_frame) >= 2,
    )


def _signed_return_sum(closes: np.ndarray, index: int) -> float | None:
    if index + N_BARS >= len(closes):
        return None
    window = closes[index:index + N_BARS + 1]
    if np.any(window <= 0):
        return None
    return float(np.sum(np.diff(np.log(window))))


def _mean_ci(
    values: np.ndarray,
) -> dict[str, float | int]:
    if len(values) < 2:
        raise RuntimeError(f"有效样本过少: n={len(values)}")
    mean = float(np.mean(values))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    boots = rng.choice(values, size=(BOOTSTRAP_N, len(values)), replace=True)
    boot_means = boots.mean(axis=1)
    return {
        "mean": mean,
        "ci95_low": float(np.percentile(boot_means, 2.5)),
        "ci95_high": float(np.percentile(boot_means, 97.5)),
        "sample_n": int(len(values)),
        "hit_rate": float(np.mean(values > 0)),
    }


def run_artifact(config: Opp16ExperimentConfig = CONFIG) -> int:
    root = _experiment_root(config)
    artifact_dir = root / "artifacts" / config.artifact_id
    artifact_path = artifact_dir / "detection_events.jsonl"
    if artifact_path.exists():
        raise FileExistsError(f"{artifact_path} 已存在；append-only")

    frame_1m = build_stitched_raw_frame("rb")
    frame_1m = frame_1m[
        (frame_1m["dt_cst"] >= pd.Timestamp(WARMUP_START))
        & (frame_1m["dt_cst"] <= pd.Timestamp(PERIOD_END))
    ].reset_index(drop=True)
    frame_5m = _build_5m_frame(frame_1m)
    period_mask = (
        (frame_5m["dt_cst"] >= pd.Timestamp(PERIOD_START))
        & (frame_5m["dt_cst"] <= pd.Timestamp(PERIOD_END))
    )

    data_dir = symbol_dir("rb")
    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    methods = sorted(
        str(value)
        for value in rollover_map["method"].dropna().unique().tolist()
    )
    roll_rule = methods[0] if len(methods) == 1 else ",".join(methods)
    used_yymms = set(frame_1m["yymm"].astype(str).tolist())
    data_fingerprint, dataset_payload = _dataset_fingerprint(
        data_dir,
        used_yymms,
        roll_rule,
    )

    detector = OPP16TwoBarReversalDetector(body_ratio=BODY_RATIO)
    context = Context(symbol="rb")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    roll_n = 0
    with artifact_path.open("x", encoding="utf-8", newline="\n") as output:
        for index in range(len(frame_5m)):
            if not bool(period_mask.iloc[index]):
                continue
            if index < 1:
                continue
            result = detector.detect(_ohlc_window(frame_5m, index), context)
            if result is None:
                continue
            roll_flag = bool(frame_5m["roll_neighborhood"].iloc[index])
            payload = {
                "bar_index": int(index),
                "timestamp": _aware_timestamp(
                    frame_5m["dt_cst"].iloc[index]
                ).isoformat(),
                "direction": result.direction.value,
                "direction_sign": (
                    1 if result.direction is Direction.LONG else -1
                ),
                "entry": result.entry,
                "stop": result.stop,
                "roll_neighborhood": roll_flag,
                "detection": result.to_dict(),
            }
            output.write(f"{canonical_json_dumps(payload)}\n")
            written += 1
            if roll_flag:
                roll_n += 1

    artifact_ref = ArtifactReference(
        artifact_id=config.artifact_id,
        uri=f"artifacts/{config.artifact_id}/detection_events.jsonl",
        content_hash=hash_file(artifact_path),
        artifact_type="detection_events",
    )
    experiment_context = ExperimentContext(
        experiment_id=config.experiment_id,
        sensor_id=config.detector_id,
        sensor_version=config.detector_version,
        parameters={"body_ratio": BODY_RATIO, "n_bars": N_BARS},
        hypothesis=config.hypothesis,
        code_revision=_git_revision(),
        data_fingerprint=data_fingerprint,
        environment_fingerprint=_environment_fingerprint(),
        subject_kind="detector",
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
    )
    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    manifest = ExperimentWorkflow(repository).build_manifest(
        experiment_context,
        artifact_refs=(artifact_ref,),
    )
    ExperimentWorkflow(repository).persist_manifest(manifest)

    metadata = {
        "experiment_id": config.experiment_id,
        "run_id": config.run_id,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "authorization": "Artifact",
        "symbol": "rb",
        "timeframe": "5m",
        "period_start": PERIOD_START.date().isoformat(),
        "period_end": PERIOD_END.date().isoformat(),
        "events_written": written,
        "roll_neighborhood_true": roll_n,
        "body_ratio": BODY_RATIO,
        "n_bars": N_BARS,
        "code_revision": experiment_context.code_revision,
        "data_fingerprint": data_fingerprint,
        "environment_fingerprint": experiment_context.environment_fingerprint,
        "parameter_fingerprint": manifest.parameter_fingerprint,
        "artifact": artifact_ref.to_dict(),
        "dataset_fingerprint_payload": dataset_payload,
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "run_metadata.json").write_text(
        f"{canonical_json_dumps(metadata)}\n",
        encoding="utf-8",
    )
    print(
        f"[ARTIFACT] {config.experiment_id} events={written} "
        f"roll={roll_n}"
    )
    print(f"  hash={artifact_ref.content_hash}")
    return 0


def _load_events(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _aligned_samples(
    events: list[dict[str, Any]],
    closes: np.ndarray,
    *,
    exclude_roll: bool,
) -> np.ndarray:
    values: list[float] = []
    for event in events:
        if exclude_roll and bool(event["roll_neighborhood"]):
            continue
        outcome = _signed_return_sum(closes, int(event["bar_index"]))
        if outcome is None:
            continue
        values.append(float(event["direction_sign"]) * outcome)
    return np.asarray(values, dtype=float)


def run_evaluation(config: Opp16ExperimentConfig = CONFIG) -> int:
    root = _experiment_root(config)
    artifact_path = (
        root / "artifacts" / config.artifact_id / "detection_events.jsonl"
    )
    if not artifact_path.is_file():
        raise FileNotFoundError(artifact_path)

    frame_1m = build_stitched_raw_frame("rb")
    frame_1m = frame_1m[
        (frame_1m["dt_cst"] >= pd.Timestamp(WARMUP_START))
        & (frame_1m["dt_cst"] <= pd.Timestamp(PERIOD_END))
    ].reset_index(drop=True)
    frame_5m = _build_5m_frame(frame_1m)
    closes = frame_5m["close"].to_numpy(dtype=float)
    events = _load_events(artifact_path)

    full_values = _aligned_samples(events, closes, exclude_roll=False)
    ex_values = _aligned_samples(events, closes, exclude_roll=True)
    full = _mean_ci(full_values)
    ex_roll = _mean_ci(ex_values)
    excluded_n = int(full["sample_n"]) - int(ex_roll["sample_n"])

    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    if repository.evaluation_exists(config.experiment_id, config.evaluation_id):
        raise FileExistsError(f"{config.evaluation_id} 已存在；append-only")

    outcome = OutcomeDefinition(
        outcome_id=config.outcome_id,
        name="aligned_SR_60",
        window={
            "bars_forward": N_BARS,
            "bar": "5m",
            "definition": "direction*sum(log_return[t+1:t+N])",
        },
        description="Direction-aligned signed return sum after OPP16 event.",
    )
    metric_full = MetricDefinition(
        metric_id=config.metric_full_id,
        name="mean_aligned_SR_60_full",
        formula_id="mean_aligned_sr_v1",
        higher_is_better=True,
        description="Mean aligned SR_60 on full event sample.",
    )
    metric_ex = MetricDefinition(
        metric_id=config.metric_ex_roll_id,
        name="mean_aligned_SR_60_ex_roll",
        formula_id="mean_aligned_sr_v1",
        higher_is_better=True,
        description="Primary mean aligned SR_60 excluding roll neighborhoods.",
    )
    artifact_hash = hash_file(artifact_path)
    outcome_record = OutcomeRecord(
        definition_id=config.outcome_id,
        values={
            "mean_aligned_ex_roll": float(ex_roll["mean"]),
            "mean_aligned_full": float(full["mean"]),
            "hit_rate_ex_roll": float(ex_roll["hit_rate"]),
            "hit_rate_full": float(full["hit_rate"]),
            "roll_excluded_n": float(excluded_n),
            "roll_excluded_fraction": (
                excluded_n / int(full["sample_n"]) if full["sample_n"] else 0.0
            ),
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
                value=float(ex_roll["mean"]),
                sample_n=float(ex_roll["sample_n"]),
            ),
            MetricRecord(
                metric_id=config.metric_full_id,
                value=float(full["mean"]),
                sample_n=float(full["sample_n"]),
            ),
        ),
        created_at=datetime.now(tz=timezone.utc),
        metadata={
            "primary_sample": "ex_roll",
            "sensitivity_sample": "full",
            "roll_window": str(DEFAULT_ROLL_WINDOW),
            "detection_artifact_hash": artifact_hash,
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
        "primary": {"sample": "ex_roll", **ex_roll},
        "sensitivity": {"sample": "full", **full},
        "roll": {
            "window": DEFAULT_ROLL_WINDOW,
            "excluded_n": excluded_n,
            "excluded_fraction": (
                excluded_n / int(full["sample_n"]) if full["sample_n"] else 0.0
            ),
        },
        "decision": "HOLD",
        "evidence": "NOT CREATED",
    }
    (root / "evaluation_report.json").write_text(
        f"{canonical_json_dumps(report)}\n",
        encoding="utf-8",
    )
    print(
        f"[EVALUATION] {config.experiment_id} "
        f"ex_roll mean={ex_roll['mean']:.6f} n={ex_roll['sample_n']} "
        f"ci=[{ex_roll['ci95_low']:.6f}, {ex_roll['ci95_high']:.6f}] "
        f"full mean={full['mean']:.6f} n={full['sample_n']}"
    )
    return 0


def run_evidence(config: Opp16ExperimentConfig = CONFIG) -> int:
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
    mean_ex = float(primary["mean"])
    mean_full = float(sensitivity["mean"])
    ci_low = float(primary["ci95_low"])
    ci_high = float(primary["ci95_high"])
    conclusion = classify_opp16_association(
        mean_ex_roll=mean_ex,
        ci95_low_ex_roll=ci_low,
        mean_full=mean_full,
        sample_n_ex_roll=int(primary["sample_n"]),
    )
    same_sign = mean_ex * mean_full > 0
    stable = abs(mean_full - mean_ex) <= MAX_ABS_DELTA_MEAN
    ci_excludes_zero_low = ci_low > 0.0

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
        subject_kind="detector",
        subject_id=config.detector_id,
        subject_version=config.detector_version,
        hypothesis=config.hypothesis,
        decision="HOLD",
        feature_artifact_uri=artifact_ref.uri,
        artifact_hash=artifact_ref.content_hash,
        created_at=created_at,
        observation={
            "detector": f"{config.detector_id}@{config.detector_version}",
            "universe": "rb/5m",
            "period": "2024-01-01..2025-12-31",
            "body_ratio": float(BODY_RATIO),
        },
        outcome={
            "name": "aligned_SR_60",
            "definition": "direction * sum(log_return[t+1:t+60])",
            "mean_aligned_ex_roll": float(
                evaluation.outcomes[0].values["mean_aligned_ex_roll"]
            ),
        },
        window={
            "n_bars": N_BARS,
            "timeframe": "5m",
            "roll_window": DEFAULT_ROLL_WINDOW,
            "primary_sample": "ex_roll",
        },
        metrics={
            "mean_aligned_ex_roll": mean_ex,
            "ci95_low_ex_roll": ci_low,
            "ci95_high_ex_roll": ci_high,
            "sample_n_ex_roll": float(primary["sample_n"]),
            "hit_rate_ex_roll": float(primary["hit_rate"]),
            "mean_aligned_full": mean_full,
            "sample_n_full": float(sensitivity["sample_n"]),
            "abs_delta_mean": abs(mean_full - mean_ex),
        },
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
        metadata={
            "evaluation_id": config.evaluation_id,
            "hypothesis_conclusion": conclusion,
            "governance_decision": "HOLD",
            "ci_lower_gt_zero": str(ci_excludes_zero_low).lower(),
            "same_sign_full_ex_roll": str(same_sign).lower(),
            "stable_abs_delta": str(stable).lower(),
            "promotion": "none",
            "lifecycle": "Candidate",
            "evidence_level_cap": "E1",
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
        "lifecycle": "Candidate",
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
