"""ATR_COMPRESSION_EXP001 Evaluation runner (no Evidence / no trading)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402
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
from strategies.paaf.evidence.repository import EvidenceRepository  # noqa: E402
from strategies.paaf.sensors.models import FeatureResult  # noqa: E402

EXPERIMENT_ID = "ATR_COMPRESSION_EXP001"
EVALUATION_ID = "EVAL-ATR-COMPRESSION-EXP001-001"
OUTCOME_ID = "OUT-ATR-EXP001-RV60"
METRIC_ID = "MET-ATR-EXP001-SPEARMAN"
ARTIFACT_ID = "ATR_COMPRESSION_EXP001_FEATURES"
N_BARS = 60
SAMPLE_INTERVAL = 60
HYPOTHESIS = (
    "atr_ratio 与未来 N-bar realized volatility 存在可检出关联 "
    "（相对 H0：无统计关联）"
)


def _load_features(path: Path) -> list[FeatureResult]:
    results: list[FeatureResult] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            results.append(FeatureResult.from_dict(json.loads(line)))
    return results


def _realized_vol(closes: np.ndarray, index: int, n: int) -> float | None:
    if index + n >= len(closes):
        return None
    window = closes[index:index + n + 1]
    if np.any(window <= 0):
        return None
    log_returns = np.diff(np.log(window))
    if log_returns.size != n:
        return None
    return float(np.std(log_returns, ddof=0))


def _tercile_means(
    atr_ratios: np.ndarray,
    rvs: np.ndarray,
) -> dict[str, float]:
    order = np.argsort(atr_ratios)
    atr_sorted = atr_ratios[order]
    rv_sorted = rvs[order]
    n = len(atr_sorted)
    cuts = (n // 3, 2 * n // 3)
    buckets = {
        "low": rv_sorted[:cuts[0]],
        "medium": rv_sorted[cuts[0]:cuts[1]],
        "high": rv_sorted[cuts[1]:],
    }
    return {
        f"mean_rv_{name}": float(np.mean(values)) if len(values) else float("nan")
        for name, values in buckets.items()
    }


def main() -> int:
    experiment_root = (
        ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID
    )
    feature_path = (
        experiment_root
        / "artifacts"
        / ARTIFACT_ID
        / "feature_results.jsonl"
    )
    if not feature_path.is_file():
        raise FileNotFoundError(feature_path)
    if (experiment_root / "evidence").exists():
        raise RuntimeError("Evidence 目录已存在；本 runner 禁止创建 Evidence")

    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    if repository.evaluation_exists(EXPERIMENT_ID, EVALUATION_ID):
        raise FileExistsError(f"{EVALUATION_ID} 已存在；append-only")
    if repository.outcome_definition_exists(EXPERIMENT_ID, OUTCOME_ID):
        raise FileExistsError(f"{OUTCOME_ID} 已存在；append-only")
    if repository.metric_definition_exists(EXPERIMENT_ID, METRIC_ID):
        raise FileExistsError(f"{METRIC_ID} 已存在；append-only")

    print("[EVAL] loading feature artifact ...")
    features = _load_features(feature_path)
    content_hash = hash_file(feature_path)
    manifest = repository.load_manifest(EXPERIMENT_ID)
    artifact_ref = next(
        ref
        for ref in manifest.artifact_refs
        if ref.artifact_id == ARTIFACT_ID
    )
    if artifact_ref.content_hash != content_hash:
        raise ValueError("Feature artifact hash 与 Manifest 不一致")

    print("[EVAL] loading closes for RV windows ...")
    frame = build_stitched_raw_frame("rb")
    first_ts = pd.Timestamp(features[0].timestamp)
    last_ts = pd.Timestamp(features[-1].timestamp)
    # Outcome may look N bars beyond last feature timestamp within frozen CbC series.
    frame = frame[frame["dt_cst"] >= first_ts].reset_index(drop=True)
    close_by_ts = {
        pd.Timestamp(ts).to_pydatetime().isoformat(): float(close)
        for ts, close in zip(frame["dt_cst"], frame["close"])
    }

    atr_values: list[float] = []
    rv_values: list[float] = []
    sample_timestamps: list[str] = []
    rejected = {
        "null_atr": 0,
        "warmup": 0,
        "rollover": 0,
        "incomplete_future": 0,
        "non_positive_price": 0,
    }

    print(
        f"[EVAL] sampling non-overlapping every {SAMPLE_INTERVAL} "
        f"from {len(features)} features ..."
    )
    for index in range(0, len(features), SAMPLE_INTERVAL):
        result = features[index]
        atr = result.values.get("atr_ratio")
        if atr is None:
            rejected["null_atr"] += 1
            continue
        if result.diagnostics.get("warmup_state") != "ready":
            rejected["warmup"] += 1
            continue
        if result.diagnostics.get("rollover_flag") != "false":
            rejected["rollover"] += 1
            continue

        stamp = result.timestamp.isoformat()
        # Locate feature bar in close series by timestamp, then take next N returns.
        matches = frame.index[frame["dt_cst"] == pd.Timestamp(result.timestamp)]
        if len(matches) == 0:
            rejected["incomplete_future"] += 1
            continue
        bar_index = int(matches[0])
        rv = _realized_vol(
            frame["close"].to_numpy(dtype=float),
            bar_index,
            N_BARS,
        )
        if rv is None:
            if bar_index + N_BARS >= len(frame):
                rejected["incomplete_future"] += 1
            else:
                rejected["non_positive_price"] += 1
            continue

        atr_values.append(float(atr))
        rv_values.append(rv)
        sample_timestamps.append(stamp)

    atr_arr = np.asarray(atr_values, dtype=float)
    rv_arr = np.asarray(rv_values, dtype=float)
    sample_n = float(len(atr_arr))
    if sample_n < 3:
        raise RuntimeError(f"有效样本过少: n={sample_n}")

    corr = spearmanr(atr_arr, rv_arr)
    rho = float(corr.correlation)
    # Optional Fisher CI (large-sample); reported only, never a pass/fail gate.
    z = np.arctanh(np.clip(rho, -0.999999, 0.999999))
    se = 1.0 / np.sqrt(max(sample_n - 3.0, 1.0))
    ci_low = float(np.tanh(z - 1.96 * se))
    ci_high = float(np.tanh(z + 1.96 * se))
    secondary = _tercile_means(atr_arr, rv_arr)

    outcome_def = OutcomeDefinition(
        outcome_id=OUTCOME_ID,
        name="future_realized_volatility_60",
        window={
            "bars_forward": N_BARS,
            "bar": "1m",
            "sampling_interval": SAMPLE_INTERVAL,
            "definition": "std(log_return[t+1:t+N])",
        },
        unit="log_return_std",
        description=(
            "Non-overlapping future 60-bar realized volatility "
            "for atr_ratio observations."
        ),
    )
    metric_def = MetricDefinition(
        metric_id=METRIC_ID,
        name="spearman_atr_ratio_vs_rv60",
        formula_id="spearman_rank_corr_v1",
        higher_is_better=None,
        description=(
            "Spearman correlation between atr_ratio and future RV_60; "
            "no significance pass/fail gate."
        ),
    )
    outcome_record = OutcomeRecord(
        definition_id=OUTCOME_ID,
        values={
            "mean_rv": float(np.mean(rv_arr)),
            "std_rv": float(np.std(rv_arr, ddof=0)),
            "mean_atr_ratio": float(np.mean(atr_arr)),
            "sampling": "non_overlapping_60",
            **{
                key: value
                for key, value in secondary.items()
                if np.isfinite(value)
            },
        },
        sample_n=sample_n,
        artifact_refs=(ARTIFACT_ID,),
    )
    metric_record = MetricRecord(
        metric_id=METRIC_ID,
        value=rho,
        sample_n=sample_n,
    )
    created_at = datetime.now(tz=timezone.utc)
    evaluation = EvaluationResult(
        evaluation_id=EVALUATION_ID,
        experiment_id=EXPERIMENT_ID,
        evidence_id=None,
        hypothesis=HYPOTHESIS,
        decision="HOLD",
        outcome_refs=(OUTCOME_ID,),
        metric_refs=(METRIC_ID,),
        outcomes=(outcome_record,),
        metrics=(metric_record,),
        created_at=created_at,
        metadata={
            "authorization": "Evaluation only; Evidence not authorized",
            "primary_metric": METRIC_ID,
            "spearman_rho": f"{rho:.10f}",
            "spearman_ci95_low": f"{ci_low:.10f}",
            "spearman_ci95_high": f"{ci_high:.10f}",
            "sample_n": str(int(sample_n)),
            "sample_interval": str(SAMPLE_INTERVAL),
            "n_bars": str(N_BARS),
            "secondary_analysis": "atr_ratio_tercile_mean_rv",
            "feature_artifact_hash": content_hash,
            "feature_last_ts": last_ts.isoformat(),
            "note": (
                "HOLD means evaluation recorded without Evidence conclusion; "
                "not a KEEP/FAIL gate."
            ),
        },
    )

    print("[EVAL] persisting Outcome/Metric definitions + EvaluationResult ...")
    repository.save_outcome_definition(EXPERIMENT_ID, outcome_def)
    repository.save_metric_definition(EXPERIMENT_ID, metric_def)
    repository.save_evaluation(evaluation)

    report = {
        "experiment_id": EXPERIMENT_ID,
        "evaluation_id": EVALUATION_ID,
        "created_at": created_at.isoformat(),
        "authorization": "Evaluation Artifact only",
        "evidence_authorized": False,
        "primary": {
            "metric": "Spearman(atr_ratio, RV_60)",
            "rho": rho,
            "ci95": [ci_low, ci_high],
            "sample_n": int(sample_n),
            "sampling": {
                "feature": "every_bar",
                "outcome_interval": SAMPLE_INTERVAL,
                "n": N_BARS,
            },
        },
        "secondary": {
            "label": "secondary",
            "atr_ratio_tercile_mean_rv": secondary,
            "note": "Must not replace primary conclusion.",
        },
        "filters_rejected": rejected,
        "first_sample_ts": sample_timestamps[0],
        "last_sample_ts": sample_timestamps[-1],
        "close_lookup_size": len(close_by_ts),
        "decision": "HOLD",
        "evidence": "NOT CREATED",
    }
    report_path = experiment_root / "evaluation_report.json"
    with report_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{canonical_json_dumps(report)}\n")

    print("[EVAL] complete")
    print(f"  rho={rho:.6f} ci95=[{ci_low:.6f}, {ci_high:.6f}] n={int(sample_n)}")
    print(f"  secondary={secondary}")
    print(f"  rejected={rejected}")
    print(f"  decision=HOLD (not Evidence)")
    print("  evidence=NOT CREATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
