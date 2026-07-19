# DATA_CONTINUOUS_CONTRACT_EXP002 multi-symbol Method A roll audit runners.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import platform
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402
from strategies.paaf.data_audit.roll_audit import (  # noqa: E402
    compute_roll_gaps,
    summarize_roll_audit,
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
from tools.tq_paths import resolve_symbol  # noqa: E402

EXPERIMENT_ID = "DATA_CONTINUOUS_CONTRACT_EXP002"
RUN_ID = "DATA_CONTINUOUS_CONTRACT_EXP002_RUN001"
ARTIFACT_ID = "DATA_CONTINUOUS_CONTRACT_EXP002_ROLL_AUDIT"
EVALUATION_ID = "EVAL-DATA-CONTINUOUS-CONTRACT-EXP002-001"
EVIDENCE_ID = "EV-DATA-CONTINUOUS-CONTRACT-EXP002-001"
OUTCOME_ID = "OUT-DATA-EXP002-ROLL-STRUCTURE"
SUBJECT_ID = "multi_cbc_unadjusted_hc_i_m_au"
SUBJECT_VERSION = "1.0"
SYMBOLS = ("hc", "i", "m", "au")
CST = ZoneInfo("Asia/Shanghai")
PERIOD_START = datetime(2024, 1, 1, tzinfo=CST)
PERIOD_END = datetime(2025, 12, 31, 23, 59, 59, tzinfo=CST)
WINDOW = 60
VOL_RATIO_GATE = 1.50
P95_RATIO_GATE = 1.20
HYPOTHESIS = (
    "预注册多品种换月邻域相对非换月存在可度量实质结构差异"
    "（相对 H0：多数品种无实质扭曲）"
)


@dataclass(frozen=True)
class SymbolAudit:
    symbol: str
    roll_count: int
    gap_abs_mean: float
    vol_ratio: float
    abs_return_p95_ratio: float
    material: bool
    bars: int
    rolls: tuple[dict[str, object], ...]


def _git_revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _file_entry(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "relative_path": path.relative_to(ROOT).as_posix(),
        "size": int(stat.st_size),
        "hash": hash_file(path),
        "modified_time": datetime.fromtimestamp(
            stat.st_mtime,
            tz=timezone.utc,
        ).isoformat(),
    }


def _symbol_fingerprint(symbol: str, used_yymms: set[str]) -> dict[str, object]:
    data_dir, file_prefix = resolve_symbol(symbol)
    files = [
        data_dir / "rollover_map.parquet",
        data_dir / "manifest.json",
    ]
    for yymm in sorted(used_yymms):
        path = data_dir / f"{file_prefix}_{yymm}.parquet"
        if not path.is_file():
            raise FileNotFoundError(path)
        files.append(path)
    manifest = [_file_entry(path) for path in files]
    return {
        "symbol": symbol,
        "source_id": f"tqsdk_offline / {symbol} / 1m / CbC",
        "file_manifest": manifest,
        "file_hashes": {
            str(item["relative_path"]): item["hash"] for item in manifest
        },
    }


def _is_material(vol_ratio: float, p95_ratio: float, roll_count: int) -> bool:
    if roll_count < 1:
        return False
    if not math.isfinite(vol_ratio) or not math.isfinite(p95_ratio):
        return False
    return vol_ratio >= VOL_RATIO_GATE or p95_ratio >= P95_RATIO_GATE


def _audit_symbol(symbol: str) -> tuple[SymbolAudit, dict[str, object]]:
    frame = build_stitched_raw_frame(symbol)
    frame = frame[
        (frame["dt_cst"] >= pd.Timestamp(PERIOD_START))
        & (frame["dt_cst"] <= pd.Timestamp(PERIOD_END))
    ].reset_index(drop=True)
    if frame.empty:
        raise RuntimeError(f"{symbol}: 区间内无 bar")

    closes = frame["close"].astype(float).tolist()
    opens = frame["open"].astype(float).tolist()
    yymms = frame["yymm"].astype(str).tolist()
    timestamps = [ts.to_pydatetime() for ts in frame["dt_cst"].tolist()]
    gaps = compute_roll_gaps(closes, opens, yymms, timestamps)
    summary = summarize_roll_audit(
        closes=closes,
        gaps=gaps,
        window=WINDOW,
    )
    material = _is_material(
        summary.vol_ratio,
        summary.abs_return_p95_ratio,
        summary.roll_count,
    )
    audit = SymbolAudit(
        symbol=symbol,
        roll_count=summary.roll_count,
        gap_abs_mean=float(summary.gap_abs_mean),
        vol_ratio=float(summary.vol_ratio),
        abs_return_p95_ratio=float(summary.abs_return_p95_ratio),
        material=material,
        bars=len(frame),
        rolls=tuple(
            {
                "roll_index": gap.roll_index,
                "timestamp": gap.timestamp.isoformat(),
                "from_yymm": gap.from_yymm,
                "to_yymm": gap.to_yymm,
                "prev_close": gap.prev_close,
                "next_open": gap.next_open,
                "gap_abs": gap.gap_abs,
                "gap_rel": gap.gap_rel,
            }
            for gap in gaps
        ),
    )
    fingerprint = _symbol_fingerprint(symbol, set(yymms))
    return audit, fingerprint


def classify_multi(
    material_count: int,
    symbol_count: int,
) -> str:
    if symbol_count <= 0:
        raise ValueError("symbol_count 必须为正")
    if material_count == 0:
        return "roll_effect_immaterial_multi"
    if material_count / symbol_count >= 0.5:
        return "roll_effect_material_annotate_multi"
    return "inconclusive"


def experiment_root() -> Path:
    return ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID


def run_artifact() -> int:
    root = experiment_root()
    artifact_path = root / "artifacts" / ARTIFACT_ID / "roll_audit.json"
    if artifact_path.exists() or (root / "manifest.json").exists():
        raise FileExistsError(f"{EXPERIMENT_ID} 已存在产物；append-only")

    audits: list[SymbolAudit] = []
    fingerprints: list[dict[str, object]] = []
    for symbol in SYMBOLS:
        print(f"[DATA EXP002] auditing {symbol} ...")
        audit, fingerprint = _audit_symbol(symbol)
        audits.append(audit)
        fingerprints.append(fingerprint)
        print(
            f"  rolls={audit.roll_count} vol_ratio={audit.vol_ratio:.4f} "
            f"p95_ratio={audit.abs_return_p95_ratio:.4f} "
            f"material={audit.material}"
        )

    material_symbols = [item.symbol for item in audits if item.material]
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "method": "CbC_unadjusted",
        "neighborhood_w": WINDOW,
        "period_start": PERIOD_START.date().isoformat(),
        "period_end": PERIOD_END.date().isoformat(),
        "symbols": list(SYMBOLS),
        "gates": {
            "vol_ratio": VOL_RATIO_GATE,
            "abs_return_p95_ratio": P95_RATIO_GATE,
            "majority_fraction": 0.5,
        },
        "per_symbol": [
            {
                "symbol": item.symbol,
                "bars": item.bars,
                "roll_count": item.roll_count,
                "gap_abs_mean": item.gap_abs_mean,
                "vol_ratio": item.vol_ratio,
                "abs_return_p95_ratio": item.abs_return_p95_ratio,
                "material": item.material,
                "rolls": list(item.rolls),
            }
            for item in audits
        ],
        "summary": {
            "symbol_count": len(SYMBOLS),
            "material_count": len(material_symbols),
            "material_symbols": material_symbols,
            "material_fraction": len(material_symbols) / len(SYMBOLS),
        },
        "dataset_fingerprints": fingerprints,
    }
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        f"{canonical_json_dumps(payload)}\n",
        encoding="utf-8",
    )
    artifact_ref = ArtifactReference(
        artifact_id=ARTIFACT_ID,
        uri=f"artifacts/{ARTIFACT_ID}/roll_audit.json",
        content_hash=hash_file(artifact_path),
        artifact_type="roll_audit",
    )
    data_fingerprint = hash_canonical_json(
        {
            "symbols": list(SYMBOLS),
            "fingerprints": fingerprints,
            "period_start": PERIOD_START.date().isoformat(),
            "period_end": PERIOD_END.date().isoformat(),
            "neighborhood_w": WINDOW,
        }
    )
    context = ExperimentContext(
        experiment_id=EXPERIMENT_ID,
        sensor_id=SUBJECT_ID,
        sensor_version=SUBJECT_VERSION,
        parameters={
            "method": "CbC_unadjusted",
            "neighborhood_w": WINDOW,
            "symbols": ",".join(SYMBOLS),
        },
        hypothesis=HYPOTHESIS,
        code_revision=_git_revision(),
        data_fingerprint=data_fingerprint,
        environment_fingerprint=hash_canonical_json(
            {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "numpy": np.__version__,
                "pandas": pd.__version__,
            }
        ),
        subject_kind="dataset",
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
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "authorization": "Artifact",
        "summary": payload["summary"],
        "artifact": artifact_ref.to_dict(),
        "code_revision": context.code_revision,
        "data_fingerprint": data_fingerprint,
    }
    (root / "run_metadata.json").write_text(
        f"{canonical_json_dumps(metadata)}\n",
        encoding="utf-8",
    )
    print(f"[DATA EXP002] artifact complete material={material_symbols}")
    return 0


def run_evaluation() -> int:
    root = experiment_root()
    artifact_path = root / "artifacts" / ARTIFACT_ID / "roll_audit.json"
    if not artifact_path.is_file():
        raise FileNotFoundError(artifact_path)
    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    if repository.evaluation_exists(EXPERIMENT_ID, EVALUATION_ID):
        raise FileExistsError(f"{EVALUATION_ID} 已存在")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    content_hash = hash_file(artifact_path)
    manifest = repository.load_manifest(EXPERIMENT_ID)
    artifact_ref = next(
        ref
        for ref in manifest.artifact_refs
        if ref.artifact_id == ARTIFACT_ID
    )
    if artifact_ref.content_hash != content_hash:
        raise ValueError("Artifact hash 与 Manifest 不一致")

    summary = artifact["summary"]
    material_count = float(summary["material_count"])
    symbol_count = float(summary["symbol_count"])
    outcome = OutcomeDefinition(
        outcome_id=OUTCOME_ID,
        name="multi_symbol_roll_neighborhood_structure",
        window={
            "neighborhood_w": WINDOW,
            "bar": "1m",
            "symbols": ",".join(SYMBOLS),
        },
        unit="ratio",
        description="Per-symbol roll structure and majority material count.",
    )
    metric_defs = (
        MetricDefinition(
            metric_id="MET-DATA-EXP002-MATERIAL-COUNT",
            name="material_symbol_count",
            formula_id="count_symbols_meeting_vol_or_p95_gate_v1",
            higher_is_better=None,
            description="Count of pre-registered symbols meeting material gates.",
        ),
        MetricDefinition(
            metric_id="MET-DATA-EXP002-MATERIAL-FRACTION",
            name="material_symbol_fraction",
            formula_id="material_count_over_symbol_count_v1",
            higher_is_better=None,
            description="Fraction of material symbols among frozen universe.",
        ),
    )
    evaluation = EvaluationResult(
        evaluation_id=EVALUATION_ID,
        experiment_id=EXPERIMENT_ID,
        evidence_id=None,
        hypothesis=HYPOTHESIS,
        decision="HOLD",
        outcome_refs=(OUTCOME_ID,),
        metric_refs=tuple(item.metric_id for item in metric_defs),
        outcomes=(
            OutcomeRecord(
                definition_id=OUTCOME_ID,
                values={
                    "material_count": material_count,
                    "symbol_count": symbol_count,
                    "material_fraction": float(summary["material_fraction"]),
                    "material_symbols": ",".join(summary["material_symbols"]),
                },
                sample_n=symbol_count,
                artifact_refs=(ARTIFACT_ID,),
            ),
        ),
        metrics=(
            MetricRecord(
                metric_id="MET-DATA-EXP002-MATERIAL-COUNT",
                value=material_count,
                sample_n=symbol_count,
            ),
            MetricRecord(
                metric_id="MET-DATA-EXP002-MATERIAL-FRACTION",
                value=float(summary["material_fraction"]),
                sample_n=symbol_count,
            ),
        ),
        created_at=datetime.now(tz=timezone.utc),
        metadata={
            "vol_ratio_gate": str(VOL_RATIO_GATE),
            "p95_ratio_gate": str(P95_RATIO_GATE),
            "feature_artifact_hash": content_hash,
        },
    )
    repository.save_outcome_definition(EXPERIMENT_ID, outcome)
    for metric in metric_defs:
        repository.save_metric_definition(EXPERIMENT_ID, metric)
    repository.save_evaluation(evaluation)
    report = {
        "experiment_id": EXPERIMENT_ID,
        "evaluation_id": EVALUATION_ID,
        "created_at": evaluation.created_at.isoformat(),
        "summary": summary,
        "per_symbol": [
            {
                "symbol": item["symbol"],
                "roll_count": item["roll_count"],
                "vol_ratio": item["vol_ratio"],
                "abs_return_p95_ratio": item["abs_return_p95_ratio"],
                "material": item["material"],
            }
            for item in artifact["per_symbol"]
        ],
        "decision": "HOLD",
        "evidence": "NOT CREATED",
    }
    (root / "evaluation_report.json").write_text(
        f"{canonical_json_dumps(report)}\n",
        encoding="utf-8",
    )
    print(
        f"[DATA EXP002 EVAL] material={int(material_count)}/{int(symbol_count)}"
    )
    return 0


def run_evidence() -> int:
    root = experiment_root()
    report_path = root / "evaluation_report.json"
    if not report_path.is_file():
        raise FileNotFoundError(report_path)
    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    if repository.evidence_exists(EXPERIMENT_ID, EVIDENCE_ID):
        raise FileExistsError(f"{EVIDENCE_ID} 已存在")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary = report["summary"]
    conclusion = classify_multi(
        int(summary["material_count"]),
        int(summary["symbol_count"]),
    )
    manifest = repository.load_manifest(EXPERIMENT_ID)
    artifact_ref = next(
        ref
        for ref in manifest.artifact_refs
        if ref.artifact_id == ARTIFACT_ID
    )
    created_at = datetime.now(tz=timezone.utc)
    evidence = EvidenceRecord(
        evidence_id=EVIDENCE_ID,
        experiment_id=EXPERIMENT_ID,
        subject_kind="dataset",
        subject_id=SUBJECT_ID,
        subject_version=SUBJECT_VERSION,
        hypothesis=HYPOTHESIS,
        decision="HOLD",
        feature_artifact_uri=artifact_ref.uri,
        artifact_hash=artifact_ref.content_hash,
        created_at=created_at,
        observation={
            "method": "CbC_unadjusted",
            "universe": "hc,i,m,au / 1m",
            "period": "2024-01-01..2025-12-31",
            "prior_rb_evidence": "EV-DATA-CONTINUOUS-CONTRACT-EXP001-RUN002",
        },
        outcome={
            "name": "multi_symbol_roll_structure",
            "hypothesis_conclusion": conclusion,
            "material_count": float(summary["material_count"]),
            "symbol_count": float(summary["symbol_count"]),
        },
        window={
            "neighborhood_w": WINDOW,
            "bar": "1m",
            "vol_ratio_gate": VOL_RATIO_GATE,
            "p95_ratio_gate": P95_RATIO_GATE,
        },
        metrics={
            "material_count": float(summary["material_count"]),
            "material_fraction": float(summary["material_fraction"]),
        },
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
        metadata={
            "evaluation_id": EVALUATION_ID,
            "hypothesis_conclusion": conclusion,
            "governance_decision": "HOLD",
            "decision_001": "unchanged",
            "promotion": "none",
            "material_symbols": ",".join(summary["material_symbols"]),
        },
    )
    repository.save_evidence(evidence)
    summary_out = {
        "evidence_id": EVIDENCE_ID,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_conclusion": conclusion,
        "governance_decision": "HOLD",
        "material_count": summary["material_count"],
        "material_symbols": summary["material_symbols"],
        "per_symbol": report["per_symbol"],
        "decision_001": "unchanged",
        "created_at": created_at.isoformat(),
    }
    (root / "evidence_summary.json").write_text(
        f"{canonical_json_dumps(summary_out)}\n",
        encoding="utf-8",
    )
    print(f"[DATA EXP002 EVIDENCE] conclusion={conclusion} HOLD")
    return 0
