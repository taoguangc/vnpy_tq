"""Write DATA_CONTINUOUS_CONTRACT_EXP001 Evidence for valid RUN002."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.paaf.evidence.hashing import canonical_json_dumps  # noqa: E402
from strategies.paaf.evidence.models import (  # noqa: E402
    EvidenceRecord,
    ExperimentManifest,
)
from strategies.paaf.evidence.repository import EvidenceRepository  # noqa: E402

EXPERIMENT_ID = "DATA_CONTINUOUS_CONTRACT_EXP001"
RUN_ID = "DATA_CONTINUOUS_CONTRACT_EXP001_RUN002"
INVALID_RUN_ID = "DATA_CONTINUOUS_CONTRACT_EXP001_RUN001"
EVALUATION_ID = "EVAL-DATA-CONTINUOUS-CONTRACT-EXP001-RUN002"
EVIDENCE_ID = "EV-DATA-CONTINUOUS-CONTRACT-EXP001-RUN002"
ARTIFACT_ID = "DATA_CONTINUOUS_CONTRACT_EXP001_RUN002_ROLL_AUDIT"
HYPOTHESIS = (
    "换月邻域的跳空/波动对全样本收益与 Feature 观测存在可度量结构差异"
    "（相对 H0：无实质扭曲）"
)


def main() -> int:
    experiment_root = (
        ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID
    )
    invalid_marker = experiment_root / "RUN001_INVALID.json"
    run_manifest_path = (
        experiment_root / "runs" / RUN_ID / "manifest.json"
    )
    if not invalid_marker.is_file():
        raise FileNotFoundError("缺少 RUN001_INVALID.json")
    if not run_manifest_path.is_file():
        raise FileNotFoundError(run_manifest_path)

    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    if repository.evidence_exists(EXPERIMENT_ID, EVIDENCE_ID):
        raise FileExistsError(f"{EVIDENCE_ID} 已存在；append-only")

    evaluation = repository.load_evaluation(EXPERIMENT_ID, EVALUATION_ID)
    if evaluation.metadata.get("source_run_id") != RUN_ID:
        raise ValueError("Evaluation 不是来自 RUN002")
    if evaluation.metadata.get("invalid_run_excluded") != INVALID_RUN_ID:
        raise ValueError("Evaluation 未显式排除 RUN001")

    run_manifest = ExperimentManifest.from_dict(
        json.loads(run_manifest_path.read_text(encoding="utf-8"))
    )
    artifact_ref = next(
        ref
        for ref in run_manifest.artifact_refs
        if ref.artifact_id == ARTIFACT_ID
    )
    outcomes = evaluation.outcomes[0].values
    metrics = {
        record.metric_id: record.value for record in evaluation.metrics
    }
    gap_abs_mean = float(
        metrics["MET-DATA-EXP001-GAP-ABS-MEAN"]
    )
    vol_ratio = float(metrics["MET-DATA-EXP001-VOL-RATIO"])
    p95_ratio = float(
        metrics["MET-DATA-EXP001-ABS-RET-P95-RATIO"]
    )

    # The effect is operationally material in this frozen sample:
    # neighborhood vol is 2.56x and p95 |return| is 1.36x non-roll.
    # This does not justify adjusted prices; it justifies explicit roll
    # diagnostics/filtering while retaining the unadjusted live-price baseline.
    hypothesis_conclusion = "roll_effect_material_annotate"
    governance_decision = "HOLD"
    created_at = datetime.now(tz=timezone.utc)
    evidence = EvidenceRecord(
        evidence_id=EVIDENCE_ID,
        experiment_id=EXPERIMENT_ID,
        subject_kind="dataset",
        subject_id="rb_cbc_unadjusted",
        subject_version="1.0",
        hypothesis=HYPOTHESIS,
        decision=governance_decision,
        feature_artifact_uri=artifact_ref.uri,
        artifact_hash=artifact_ref.content_hash,
        created_at=created_at,
        observation={
            "method": "CbC_unadjusted",
            "universe": "rb/1m",
            "period": "2024-01-01..2025-12-31",
            "source_run_id": RUN_ID,
            "invalid_run_excluded": INVALID_RUN_ID,
        },
        outcome={
            "name": "roll_neighborhood_structure",
            "gap_definition": "old_close_to_new_open",
            "roll_count": float(outcomes["roll_count"]),
            "hypothesis_conclusion": hypothesis_conclusion,
        },
        window={
            "neighborhood_w": 60,
            "bar": "1m",
            "sampling": "roll_neighborhood_vs_non_roll",
        },
        metrics={
            "gap_abs_mean": gap_abs_mean,
            "gap_abs_median": float(outcomes["gap_abs_median"]),
            "gap_rel_mean": float(outcomes["gap_rel_mean"]),
            "vol_ratio": vol_ratio,
            "abs_return_p95_ratio": p95_ratio,
            "atr_ratio_neighborhood_mean": float(
                outcomes["secondary_atr_ratio_neighborhood_mean"]
            ),
            "atr_ratio_non_roll_mean": float(
                outcomes["secondary_atr_ratio_non_roll_mean"]
            ),
            "sample_n_neighborhood": float(
                outcomes["sample_n_neighborhood"]
            ),
            "sample_n_non_roll": float(
                outcomes["sample_n_non_roll"]
            ),
        },
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
        metadata={
            "evaluation_id": EVALUATION_ID,
            "hypothesis_conclusion": hypothesis_conclusion,
            "governance_decision": governance_decision,
            "baseline": "Decision 001 unchanged",
            "baseline_change": "none",
            "production_loader_change": "none",
            "required_action": (
                "Keep CbC unadjusted; require rollover diagnostics and "
                "pre-registered filtering for roll-sensitive Feature studies."
            ),
            "secondary_interpretation": (
                "atr_ratio mean 1.1384 in roll neighborhoods vs 1.0085 "
                "outside; secondary only."
            ),
            "limitations": (
                "Single symbol rb, six roll events, 2024-2025; "
                "no adjusted-price controls and no trading evaluation."
            ),
            "note": (
                "HOLD means retain frozen baseline and annotate material "
                "roll effects; no promotion or automatic protocol change."
            ),
        },
    )
    repository.save_evidence(evidence)

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "source_run_id": RUN_ID,
        "evidence_id": EVIDENCE_ID,
        "evaluation_id": EVALUATION_ID,
        "created_at": created_at.isoformat(),
        "hypothesis_conclusion": hypothesis_conclusion,
        "governance_decision": governance_decision,
        "baseline_change": "none",
        "decision_001": "unchanged",
        "production_loader_change": "none",
        "metrics": {
            "gap_abs_mean": gap_abs_mean,
            "vol_ratio": vol_ratio,
            "abs_return_p95_ratio": p95_ratio,
        },
        "sensor_status_change": "none",
        "trading": "none",
    }
    summary_path = (
        experiment_root / "runs" / RUN_ID / "evidence_summary.json"
    )
    with summary_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{canonical_json_dumps(summary)}\n")

    print("[DATA EVIDENCE] complete")
    print(f"  evidence_id={EVIDENCE_ID}")
    print(f"  conclusion={hypothesis_conclusion}")
    print(f"  decision={governance_decision}")
    print("  Decision 001=UNCHANGED")
    print("  production loader change=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
