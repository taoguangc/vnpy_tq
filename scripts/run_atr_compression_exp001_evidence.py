"""Write ATR_COMPRESSION_EXP001 EvidenceRecord (no promotion / no trading)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.paaf.evidence.hashing import canonical_json_dumps  # noqa: E402
from strategies.paaf.evidence.models import EvidenceRecord  # noqa: E402
from strategies.paaf.evidence.repository import EvidenceRepository  # noqa: E402

EXPERIMENT_ID = "ATR_COMPRESSION_EXP001"
EVIDENCE_ID = "EV-ATR-COMPRESSION-EXP001-001"
EVALUATION_ID = "EVAL-ATR-COMPRESSION-EXP001-001"
ARTIFACT_ID = "ATR_COMPRESSION_EXP001_FEATURES"
HYPOTHESIS = (
    "atr_ratio 与未来 N-bar realized volatility 存在可检出关联 "
    "（相对 H0：无统计关联）"
)


def main() -> int:
    experiment_root = (
        ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID
    )
    report_path = experiment_root / "evaluation_report.json"
    if not report_path.is_file():
        raise FileNotFoundError(report_path)

    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    if repository.evidence_exists(EXPERIMENT_ID, EVIDENCE_ID):
        raise FileExistsError(f"{EVIDENCE_ID} 已存在；append-only")

    manifest = repository.load_manifest(EXPERIMENT_ID)
    evaluation = repository.load_evaluation(EXPERIMENT_ID, EVALUATION_ID)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    artifact_ref = next(
        ref for ref in manifest.artifact_refs if ref.artifact_id == ARTIFACT_ID
    )

    primary = report["primary"]
    rho = float(primary["rho"])
    sample_n = float(primary["sample_n"])
    ci_low, ci_high = primary["ci95"]
    secondary = report["secondary"]["atr_ratio_tercile_mean_rv"]

    # RQ4: no pass/fail gate. Weak |ρ|, flat secondary buckets, single-symbol
    # E1 only, and sign does not support compression→expansion narrative.
    # Registered H1 is association-only; still default to inconclusive unless
    # effect and robustness are crystal clear.
    hypothesis_conclusion = "inconclusive"
    governance_decision = "HOLD"

    created_at = datetime.now(tz=timezone.utc)
    evidence = EvidenceRecord(
        evidence_id=EVIDENCE_ID,
        experiment_id=EXPERIMENT_ID,
        subject_kind="feature_sensor",
        subject_id=manifest.sensor_id,
        subject_version=manifest.sensor_version,
        hypothesis=HYPOTHESIS,
        decision=governance_decision,
        feature_artifact_uri=artifact_ref.uri,
        artifact_hash=artifact_ref.content_hash,
        created_at=created_at,
        observation={
            "feature": "atr_ratio",
            "sensor": f"{manifest.sensor_id}@{manifest.sensor_version}",
            "universe": "rb/1m",
            "period": "2024-01-01..2025-12-31",
        },
        outcome={
            "name": "RV_60",
            "definition": "std(log_return[t+1:t+N])",
            "mean_rv": float(evaluation.outcomes[0].values["mean_rv"]),
        },
        window={
            "n_bars": 60,
            "sampling_interval": 60,
            "sampling": "non_overlapping",
            "bar": "1m",
        },
        metrics={
            "spearman_rho": rho,
            "spearman_ci95_low": float(ci_low),
            "spearman_ci95_high": float(ci_high),
            "sample_n": sample_n,
            "secondary_mean_rv_low": float(secondary["mean_rv_low"]),
            "secondary_mean_rv_medium": float(secondary["mean_rv_medium"]),
            "secondary_mean_rv_high": float(secondary["mean_rv_high"]),
        },
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
        metadata={
            "evaluation_id": EVALUATION_ID,
            "hypothesis_conclusion": hypothesis_conclusion,
            "governance_decision": governance_decision,
            "promotion": "none",
            "production_enablement": "false",
            "rationale": (
                "Weak positive Spearman (rho~0.11); CI excludes 0 but effect "
                "is small; secondary terciles nearly flat; single-symbol E1 "
                "only; sign does not support compression->expansion narrative; "
                "RQ4 forbids significance pass/fail as promotion gate."
            ),
            "note": (
                "hypothesis_conclusion=inconclusive; "
                "decision=HOLD means no KEEP/REVERT promotion action; "
                "Sensor remains EXPERIMENT."
            ),
        },
    )

    repository.save_evidence(evidence)

    summary = {
        "evidence_id": EVIDENCE_ID,
        "experiment_id": EXPERIMENT_ID,
        "evaluation_id": EVALUATION_ID,
        "hypothesis_conclusion": hypothesis_conclusion,
        "governance_decision": governance_decision,
        "spearman_rho": rho,
        "sample_n": int(sample_n),
        "promotion": "none",
        "sensor_status": "EXPERIMENT",
        "created_at": created_at.isoformat(),
    }
    summary_path = experiment_root / "evidence_summary.json"
    with summary_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{canonical_json_dumps(summary)}\n")

    print("[EVIDENCE] complete")
    print(f"  evidence_id={EVIDENCE_ID}")
    print(f"  hypothesis_conclusion={hypothesis_conclusion}")
    print(f"  governance_decision={governance_decision}")
    print("  promotion=none")
    print("  sensor_status=EXPERIMENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
