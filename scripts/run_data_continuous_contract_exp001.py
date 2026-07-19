"""DATA_CONTINUOUS_CONTRACT_EXP001 Method A runner (artifact only; no Evaluation)."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
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
from strategies.paaf.evidence.hashing import (  # noqa: E402
    canonical_json_dumps,
    hash_canonical_json,
    hash_file,
)
from strategies.paaf.evidence.models import ArtifactReference  # noqa: E402
from strategies.paaf.evidence.repository import EvidenceRepository  # noqa: E402
from strategies.paaf.evidence.workflow import (  # noqa: E402
    ExperimentContext,
    ExperimentWorkflow,
)
from strategies.paaf.sensors.atr_compression import (  # noqa: E402
    ATRCompressionSensor,
    DEFAULT_ATR_PERIOD,
    DEFAULT_BASELINE_WINDOW,
)
from tools.tq_paths import symbol_dir  # noqa: E402

EXPERIMENT_ID = "DATA_CONTINUOUS_CONTRACT_EXP001"
RUN_ID = "DATA_CONTINUOUS_CONTRACT_EXP001_RUN001"
ARTIFACT_ID = "DATA_CONTINUOUS_CONTRACT_EXP001_ROLL_AUDIT"
SUBJECT_ID = "rb_cbc_unadjusted"
SUBJECT_VERSION = "1.0"
CST = ZoneInfo("Asia/Shanghai")
PERIOD_START = datetime(2024, 1, 1, tzinfo=CST)
PERIOD_END = datetime(2025, 12, 31, 23, 59, 59, tzinfo=CST)
WARMUP_START = datetime(2023, 12, 1, tzinfo=CST)
WINDOW = 60
PARAMETERS = {
    "method": "CbC_unadjusted",
    "neighborhood_w": WINDOW,
    "atr_period": DEFAULT_ATR_PERIOD,
    "baseline_window": DEFAULT_BASELINE_WINDOW,
}
HYPOTHESIS = (
    "换月邻域的跳空/波动对全样本收益与 Feature 观测存在可度量结构差异"
    "（相对 H0：无实质扭曲）"
)


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
) -> tuple[str, dict[str, object]]:
    files: list[Path] = [
        data_dir / "rollover_map.parquet",
        data_dir / "manifest.json",
    ]
    for yymm in sorted(used_yymms):
        path = data_dir / f"rb_{yymm}.parquet"
        if not path.is_file():
            raise FileNotFoundError(path)
        files.append(path)
    file_manifest = [_file_entry(path, relative_to=ROOT) for path in files]
    payload = {
        "source_id": "tqsdk_offline / rb / 1m / CbC",
        "file_manifest": file_manifest,
        "file_hashes": {
            item["relative_path"]: item["hash"] for item in file_manifest
        },
        "construction_metadata": {
            "continuous_contract": "CbC",
            "adjustment": "unadjusted",
            "bar": "1m",
            "neighborhood_w": WINDOW,
            "period_start": PERIOD_START.date().isoformat(),
            "period_end": PERIOD_END.date().isoformat(),
            "data_spec": "docs/07_DATA_SPEC.md@1.0.0",
        },
    }
    return hash_canonical_json(payload), payload


def _environment_fingerprint() -> str:
    return hash_canonical_json(
        {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        }
    )


def _compute_atr_ratios(frame: pd.DataFrame) -> list[float | None]:
    sensor = ATRCompressionSensor()
    highs = frame["high"].to_numpy(dtype=float)
    lows = frame["low"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    yymms = frame["yymm"].astype(str).to_numpy()
    timestamps = frame["dt_cst"]
    lookback = DEFAULT_ATR_PERIOD + DEFAULT_BASELINE_WINDOW
    values: list[float | None] = []
    previous_yymm: str | None = None
    for index in range(len(frame)):
        current = yymms[index]
        rollover_flag = previous_yymm is not None and current != previous_yymm
        previous_yymm = current
        start = max(0, index + 1 - lookback)
        result = sensor.observe(
            symbol="rb",
            timeframe="1m",
            timestamp=timestamps.iloc[index].to_pydatetime(),
            window={
                "high": highs[start:index + 1].tolist(),
                "low": lows[start:index + 1].tolist(),
                "close": closes[start:index + 1].tolist(),
                "rollover_flag": bool(rollover_flag),
            },
            parameters={
                "atr_period": DEFAULT_ATR_PERIOD,
                "baseline_window": DEFAULT_BASELINE_WINDOW,
            },
        )
        values.append(result.values.get("atr_ratio"))
    return values


def main() -> int:
    data_dir = symbol_dir("rb")
    experiment_root = (
        ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID
    )
    artifact_path = (
        experiment_root / "artifacts" / ARTIFACT_ID / "roll_audit.json"
    )
    if artifact_path.exists() or (experiment_root / "manifest.json").exists():
        raise FileExistsError(f"{EXPERIMENT_ID} 已存在产物；append-only")

    print("[DATA EXP001] loading CbC unadjusted frame ...")
    frame = build_stitched_raw_frame("rb")
    frame = frame[
        (frame["dt_cst"] >= pd.Timestamp(WARMUP_START))
        & (frame["dt_cst"] <= pd.Timestamp(PERIOD_END))
    ].reset_index(drop=True)
    period_mask = (
        (frame["dt_cst"] >= pd.Timestamp(PERIOD_START))
        & (frame["dt_cst"] <= pd.Timestamp(PERIOD_END))
    )
    period = frame.loc[period_mask].reset_index(drop=True)
    if period.empty:
        raise RuntimeError("区间内无 bar")

    closes = period["close"].astype(float).tolist()
    yymms = period["yymm"].astype(str).tolist()
    timestamps = [
        ts.to_pydatetime() for ts in period["dt_cst"].tolist()
    ]
    gaps = compute_roll_gaps(closes, yymms, timestamps)
    # Keep rolls whose timestamp falls in period (already true by construction).
    print(f"[DATA EXP001] rolls_in_period={len(gaps)}")

    print("[DATA EXP001] computing atr_ratio secondary series ...")
    atr_ratios = _compute_atr_ratios(period)
    summary = summarize_roll_audit(
        closes=closes,
        gaps=gaps,
        window=WINDOW,
        atr_ratios=atr_ratios,
    )

    used_yymms = set(frame["yymm"].astype(str).tolist())
    data_fingerprint, dataset_payload = _dataset_fingerprint(
        data_dir,
        used_yymms,
    )
    code_revision = _git_revision()
    environment_fingerprint = _environment_fingerprint()

    artifact_payload = {
        "experiment_id": EXPERIMENT_ID,
        "method": "CbC_unadjusted",
        "neighborhood_w": WINDOW,
        "period_start": PERIOD_START.date().isoformat(),
        "period_end": PERIOD_END.date().isoformat(),
        "bars": len(period),
        "summary": {
            "roll_count": summary.roll_count,
            "gap_abs_mean": summary.gap_abs_mean,
            "gap_abs_median": summary.gap_abs_median,
            "gap_rel_mean": summary.gap_rel_mean,
            "gap_rel_median": summary.gap_rel_median,
            "neighborhood_vol": summary.neighborhood_vol,
            "non_roll_vol": summary.non_roll_vol,
            "vol_ratio": summary.vol_ratio,
            "neighborhood_abs_return_p95": summary.neighborhood_abs_return_p95,
            "non_roll_abs_return_p95": summary.non_roll_abs_return_p95,
            "abs_return_p95_ratio": summary.abs_return_p95_ratio,
            "atr_ratio_neighborhood_mean": summary.atr_ratio_neighborhood_mean,
            "atr_ratio_non_roll_mean": summary.atr_ratio_non_roll_mean,
            "sample_n_neighborhood": summary.sample_n_neighborhood,
            "sample_n_non_roll": summary.sample_n_non_roll,
        },
        "rolls": [
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
        ],
        "secondary": "atr_ratio_roll_sensitivity",
        "evaluation_authorized": False,
        "evidence_authorized": False,
    }

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{canonical_json_dumps(artifact_payload)}\n")
    content_hash = hash_file(artifact_path)
    artifact_ref = ArtifactReference(
        artifact_id=ARTIFACT_ID,
        uri=f"artifacts/{ARTIFACT_ID}/roll_audit.json",
        content_hash=content_hash,
        artifact_type="roll_audit",
    )

    # ExperimentContext historically defaults to feature_sensor; dataset is now allowed.
    context = ExperimentContext(
        experiment_id=EXPERIMENT_ID,
        sensor_id=SUBJECT_ID,
        sensor_version=SUBJECT_VERSION,
        parameters=PARAMETERS,
        hypothesis=HYPOTHESIS,
        code_revision=code_revision,
        data_fingerprint=data_fingerprint,
        environment_fingerprint=environment_fingerprint,
        subject_kind="dataset",
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
    )
    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    workflow = ExperimentWorkflow(repository)
    manifest = workflow.build_manifest(context, artifact_refs=(artifact_ref,))
    workflow.persist_manifest(manifest)

    run_metadata = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "authorization": "Roll audit Artifact only",
        "evaluation_authorized": False,
        "evidence_authorized": False,
        "code_revision": code_revision,
        "data_fingerprint": data_fingerprint,
        "environment_fingerprint": environment_fingerprint,
        "parameter_fingerprint": manifest.parameter_fingerprint,
        "artifact": artifact_ref.to_dict(),
        "dataset_fingerprint_payload": dataset_payload,
        "summary": artifact_payload["summary"],
    }
    with (experiment_root / "run_metadata.json").open(
        "x",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        handle.write(f"{canonical_json_dumps(run_metadata)}\n")

    print("[DATA EXP001] complete (artifact only)")
    print(json.dumps(artifact_payload["summary"], ensure_ascii=False, indent=2))
    print("  evaluation=NOT RUN")
    print("  evidence=NOT RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
