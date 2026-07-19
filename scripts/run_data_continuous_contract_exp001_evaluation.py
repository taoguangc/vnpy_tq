"""DATA_CONTINUOUS_CONTRACT_EXP001 Evaluation based on RUN002 only."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
from strategies.paaf.evidence.models import ExperimentManifest  # noqa: E402
from strategies.paaf.evidence.repository import EvidenceRepository  # noqa: E402

EXPERIMENT_ID = "DATA_CONTINUOUS_CONTRACT_EXP001"
RUN_ID = "DATA_CONTINUOUS_CONTRACT_EXP001_RUN002"
EVALUATION_ID = "EVAL-DATA-CONTINUOUS-CONTRACT-EXP001-RUN002"
OUTCOME_ID = "OUT-DATA-EXP001-ROLL-STRUCTURE"
METRIC_GAP = "MET-DATA-EXP001-GAP-ABS-MEAN"
METRIC_VOL = "MET-DATA-EXP001-VOL-RATIO"
METRIC_P95 = "MET-DATA-EXP001-ABS-RET-P95-RATIO"
ARTIFACT_ID = "DATA_CONTINUOUS_CONTRACT_EXP001_RUN002_ROLL_AUDIT"
HYPOTHESIS = (
    "换月邻域的跳空/波动对全样本收益与 Feature 观测存在可度量结构差异"
    "（相对 H0：无实质扭曲）"
)


def main() -> int:
    experiment_root = (
        ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID
    )
    invalid = experiment_root / "RUN001_INVALID.json"
    if not invalid.is_file():
        raise FileNotFoundError("缺少 RUN001_INVALID.json；禁止在无效 run 上评估")

    artifact_path = (
        experiment_root / "artifacts" / ARTIFACT_ID / "roll_audit.json"
    )
    run_manifest_path = (
        experiment_root / "runs" / RUN_ID / "manifest.json"
    )
    if not artifact_path.is_file():
        raise FileNotFoundError(artifact_path)
    if not run_manifest_path.is_file():
        raise FileNotFoundError(run_manifest_path)

    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    # Root manifest exists from RUN001; repository APIs require it.
    if not repository.manifest_exists(EXPERIMENT_ID):
        raise FileNotFoundError("缺少 experiment 根 manifest.json")

    if repository.evaluation_exists(EXPERIMENT_ID, EVALUATION_ID):
        raise FileExistsError(f"{EVALUATION_ID} 已存在；append-only")
    for outcome_id in (OUTCOME_ID,):
        if repository.outcome_definition_exists(EXPERIMENT_ID, outcome_id):
            raise FileExistsError(f"{outcome_id} 已存在；append-only")
    for metric_id in (METRIC_GAP, METRIC_VOL, METRIC_P95):
        if repository.metric_definition_exists(EXPERIMENT_ID, metric_id):
            raise FileExistsError(f"{metric_id} 已存在；append-only")

    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    content_hash = hash_file(artifact_path)
    run_manifest = ExperimentManifest.from_dict(
        json.loads(run_manifest_path.read_text(encoding="utf-8"))
    )
    artifact_ref = next(
        ref for ref in run_manifest.artifact_refs if ref.artifact_id == ARTIFACT_ID
    )
    if artifact_ref.content_hash != content_hash:
        raise ValueError("RUN002 Artifact hash 与 run manifest 不一致")
    if artifact.get("method") != "CbC_unadjusted":
        raise ValueError("Evaluation 仅接受 Method A")

    summary = artifact["summary"]
    sample_n = float(summary["roll_count"])
    gap_abs_mean = float(summary["gap_abs_mean"])
    vol_ratio = float(summary["vol_ratio"])
    p95_ratio = float(summary["abs_return_p95_ratio"])

    outcome_def = OutcomeDefinition(
        outcome_id=OUTCOME_ID,
        name="roll_neighborhood_structure",
        window={
            "neighborhood_w": int(artifact["neighborhood_w"]),
            "bar": "1m",
            "definition": "roll gap + neighborhood vs non-roll vol/return",
        },
        unit="ratio_or_price",
        description=(
            "Unadjusted CbC roll gaps and neighborhood return/vol "
            "structure versus non-roll bars."
        ),
    )
    metric_gap = MetricDefinition(
        metric_id=METRIC_GAP,
        name="roll_gap_abs_mean",
        formula_id="mean_abs_old_close_to_new_open_v1",
        higher_is_better=None,
        description="Mean absolute roll gap using old close -> new open.",
    )
    metric_vol = MetricDefinition(
        metric_id=METRIC_VOL,
        name="roll_neighborhood_vol_ratio",
        formula_id="std_logret_neighborhood_over_nonroll_v1",
        higher_is_better=None,
        description="Neighborhood realized vol / non-roll realized vol.",
    )
    metric_p95 = MetricDefinition(
        metric_id=METRIC_P95,
        name="roll_neighborhood_abs_return_p95_ratio",
        formula_id="p95_abs_logret_neighborhood_over_nonroll_v1",
        higher_is_better=None,
        description="Neighborhood |log-return| p95 / non-roll p95.",
    )

    outcome_record = OutcomeRecord(
        definition_id=OUTCOME_ID,
        values={
            "roll_count": float(summary["roll_count"]),
            "gap_abs_mean": gap_abs_mean,
            "gap_abs_median": float(summary["gap_abs_median"]),
            "gap_rel_mean": float(summary["gap_rel_mean"]),
            "gap_rel_median": float(summary["gap_rel_median"]),
            "neighborhood_vol": float(summary["neighborhood_vol"]),
            "non_roll_vol": float(summary["non_roll_vol"]),
            "neighborhood_abs_return_p95": float(
                summary["neighborhood_abs_return_p95"]
            ),
            "non_roll_abs_return_p95": float(summary["non_roll_abs_return_p95"]),
            "sample_n_neighborhood": float(summary["sample_n_neighborhood"]),
            "sample_n_non_roll": float(summary["sample_n_non_roll"]),
            "secondary_atr_ratio_neighborhood_mean": float(
                summary["atr_ratio_neighborhood_mean"]
            ),
            "secondary_atr_ratio_non_roll_mean": float(
                summary["atr_ratio_non_roll_mean"]
            ),
            "gap_definition": "old_close_to_new_open",
            "source_run_id": RUN_ID,
        },
        sample_n=sample_n,
        artifact_refs=(ARTIFACT_ID,),
    )
    metrics = (
        MetricRecord(metric_id=METRIC_GAP, value=gap_abs_mean, sample_n=sample_n),
        MetricRecord(metric_id=METRIC_VOL, value=vol_ratio, sample_n=sample_n),
        MetricRecord(metric_id=METRIC_P95, value=p95_ratio, sample_n=sample_n),
    )

    created_at = datetime.now(tz=timezone.utc)
    evaluation = EvaluationResult(
        evaluation_id=EVALUATION_ID,
        experiment_id=EXPERIMENT_ID,
        evidence_id=None,
        hypothesis=HYPOTHESIS,
        decision="HOLD",
        outcome_refs=(OUTCOME_ID,),
        metric_refs=(METRIC_GAP, METRIC_VOL, METRIC_P95),
        outcomes=(outcome_record,),
        metrics=metrics,
        created_at=created_at,
        notes=(
            "Evaluation of RUN002 Method A roll audit only. "
            "No Evidence conclusion and no baseline change."
        ),
        metadata={
            "authorization": "Evaluation only; Evidence not authorized",
            "source_run_id": RUN_ID,
            "invalid_run_excluded": "DATA_CONTINUOUS_CONTRACT_EXP001_RUN001",
            "artifact_hash": content_hash,
            "method": "CbC_unadjusted",
            "neighborhood_w": str(artifact["neighborhood_w"]),
            "primary_metrics": f"{METRIC_GAP},{METRIC_VOL},{METRIC_P95}",
            "secondary": "atr_ratio_roll_sensitivity",
            "vol_ratio": f"{vol_ratio:.10f}",
            "gap_abs_mean": f"{gap_abs_mean:.10f}",
            "abs_return_p95_ratio": f"{p95_ratio:.10f}",
            "note": (
                "HOLD means metrics recorded without Evidence / promotion; "
                "Decision 001 baseline remains frozen."
            ),
        },
    )

    print("[DATA EVAL] persisting definitions + EvaluationResult ...")
    repository.save_outcome_definition(EXPERIMENT_ID, outcome_def)
    repository.save_metric_definition(EXPERIMENT_ID, metric_gap)
    repository.save_metric_definition(EXPERIMENT_ID, metric_vol)
    repository.save_metric_definition(EXPERIMENT_ID, metric_p95)
    repository.save_evaluation(evaluation)

    report = {
        "experiment_id": EXPERIMENT_ID,
        "evaluation_id": EVALUATION_ID,
        "source_run_id": RUN_ID,
        "created_at": created_at.isoformat(),
        "authorization": "Evaluation Artifact only",
        "evidence_authorized": False,
        "excluded_invalid_run": "DATA_CONTINUOUS_CONTRACT_EXP001_RUN001",
        "primary": {
            "gap_abs_mean": gap_abs_mean,
            "vol_ratio": vol_ratio,
            "abs_return_p95_ratio": p95_ratio,
            "roll_count": int(sample_n),
            "gap_definition": "old_close_to_new_open",
        },
        "secondary": {
            "label": "secondary",
            "atr_ratio_neighborhood_mean": float(
                summary["atr_ratio_neighborhood_mean"]
            ),
            "atr_ratio_non_roll_mean": float(summary["atr_ratio_non_roll_mean"]),
            "note": "Must not replace primary conclusion.",
        },
        "decision": "HOLD",
        "evidence": "NOT CREATED",
        "baseline_change": "none",
    }
    report_path = (
        experiment_root / "runs" / RUN_ID / "evaluation_report.json"
    )
    with report_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{canonical_json_dumps(report)}\n")

    print("[DATA EVAL] complete")
    print(f"  evaluation_id={EVALUATION_ID}")
    print(f"  gap_abs_mean={gap_abs_mean:.4f}")
    print(f"  vol_ratio={vol_ratio:.4f}")
    print(f"  abs_return_p95_ratio={p95_ratio:.4f}")
    print("  decision=HOLD")
    print("  evidence=NOT CREATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
