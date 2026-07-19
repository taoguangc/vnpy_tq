"""ATR_COMPRESSION_EXP001 Feature Artifact runner (no Evaluation/Evidence)."""

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
from strategies.paaf.evidence.hashing import (  # noqa: E402
    canonical_json_dumps,
    hash_canonical_json,
    hash_file,
)
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
from strategies.paaf.sensors.models import FeatureResult  # noqa: E402
from tools.tq_paths import symbol_dir  # noqa: E402

EXPERIMENT_ID = "ATR_COMPRESSION_EXP001"
RUN_ID = "ATR_COMPRESSION_EXP001_RUN001"
ARTIFACT_ID = "ATR_COMPRESSION_EXP001_FEATURES"
SENSOR_ID = "atr_compression"
SENSOR_VERSION = "1.0"
SYMBOL = "rb"
TIMEFRAME = "1m"
CST = ZoneInfo("Asia/Shanghai")
PERIOD_START = datetime(2024, 1, 1, tzinfo=CST)
PERIOD_END = datetime(2025, 12, 31, 23, 59, 59, tzinfo=CST)
WARMUP_START = datetime(2023, 12, 1, tzinfo=CST)
PARAMETERS = {
    "atr_period": DEFAULT_ATR_PERIOD,
    "baseline_window": DEFAULT_BASELINE_WINDOW,
}
HYPOTHESIS = (
    "atr_ratio 与未来 N-bar realized volatility 存在可检出关联 "
    "（相对 H0：无统计关联）"
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


def _build_dataset_fingerprint(
    data_dir: Path,
    used_yymms: set[str],
    roll_rule: str,
) -> tuple[str, dict[str, object]]:
    project = ROOT
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

    file_manifest = [_file_entry(path, relative_to=project) for path in files]
    construction_metadata = {
        "continuous_contract": "CbC",
        "adjustment": "unadjusted",
        "bar": "1m",
        "roll_rule": roll_rule,
        "data_spec": "docs/07_DATA_SPEC.md@1.0.0",
        "period_start": PERIOD_START.date().isoformat(),
        "period_end": PERIOD_END.date().isoformat(),
    }
    payload = {
        "source_id": "tqsdk_offline / rb / 1m / CbC",
        "file_manifest": file_manifest,
        "file_hashes": {
            item["relative_path"]: item["hash"] for item in file_manifest
        },
        "construction_metadata": construction_metadata,
    }
    return hash_canonical_json(payload), payload


def _environment_fingerprint() -> str:
    payload = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }
    return hash_canonical_json(payload)


def _ensure_aware(ts: pd.Timestamp) -> datetime:
    value = ts.to_pydatetime()
    if value.tzinfo is None:
        return value.replace(tzinfo=CST)
    return value


def main() -> int:
    data_dir = symbol_dir("rb")
    experiment_root = ROOT / "research" / "output" / "evidence" / EXPERIMENT_ID
    artifact_path = (
        experiment_root
        / "artifacts"
        / ARTIFACT_ID
        / "feature_results.jsonl"
    )
    run_meta_path = experiment_root / "run_metadata.json"

    if artifact_path.exists() or (
        experiment_root / "manifest.json"
    ).exists():
        raise FileExistsError(
            f"{EXPERIMENT_ID} 已存在产物；append-only，禁止覆盖"
        )

    print(f"[EXP001] loading stitched frame for {SYMBOL} ...")
    frame = build_stitched_raw_frame("rb")
    frame = frame[
        (frame["dt_cst"] >= pd.Timestamp(WARMUP_START))
        & (frame["dt_cst"] <= pd.Timestamp(PERIOD_END))
    ].reset_index(drop=True)
    if frame.empty:
        raise RuntimeError("加载后无可用 bar")

    rollover_map = pd.read_parquet(data_dir / "rollover_map.parquet")
    roll_methods = sorted(
        {
            str(value)
            for value in rollover_map["method"].dropna().unique().tolist()
        }
    )
    roll_rule = roll_methods[0] if len(roll_methods) == 1 else ",".join(
        roll_methods
    )

    period_mask = (
        (frame["dt_cst"] >= pd.Timestamp(PERIOD_START))
        & (frame["dt_cst"] <= pd.Timestamp(PERIOD_END))
    )
    period_frame = frame.loc[period_mask]
    used_yymms = set(frame["yymm"].astype(str).tolist())
    data_fingerprint, dataset_payload = _build_dataset_fingerprint(
        data_dir,
        used_yymms,
        roll_rule,
    )
    code_revision = _git_revision()
    environment_fingerprint = _environment_fingerprint()

    highs = frame["high"].to_numpy(dtype=float)
    lows = frame["low"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    yymms = frame["yymm"].astype(str).to_numpy()
    timestamps = frame["dt_cst"]

    lookback = DEFAULT_ATR_PERIOD + DEFAULT_BASELINE_WINDOW
    sensor = ATRCompressionSensor()
    parameters = dict(PARAMETERS)

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    ready_n = 0
    null_n = 0
    rollover_n = 0
    written = 0

    print(
        f"[EXP001] observing {period_mask.sum()} bars "
        f"(warmup context={(~period_mask).sum()}) ..."
    )
    with artifact_path.open("x", encoding="utf-8", newline="\n") as out:
        previous_yymm: str | None = None
        for index in range(len(frame)):
            current_yymm = yymms[index]
            rollover_flag = (
                previous_yymm is not None and current_yymm != previous_yymm
            )
            previous_yymm = current_yymm
            if not bool(period_mask.iloc[index]):
                continue

            start = max(0, index + 1 - lookback)
            window = {
                "high": highs[start:index + 1].tolist(),
                "low": lows[start:index + 1].tolist(),
                "close": closes[start:index + 1].tolist(),
                "rollover_flag": bool(rollover_flag),
            }
            result = sensor.observe(
                symbol=SYMBOL,
                timeframe=TIMEFRAME,
                timestamp=_ensure_aware(timestamps.iloc[index]),
                window=window,
                parameters=parameters,
            )
            if not isinstance(result, FeatureResult):
                raise TypeError("Sensor 必须返回 FeatureResult")
            out.write(f"{canonical_json_dumps(result.to_dict())}\n")
            written += 1
            if result.values.get("atr_ratio") is None:
                null_n += 1
            else:
                ready_n += 1
            if result.diagnostics.get("rollover_flag") == "true":
                rollover_n += 1
            if written % 20000 == 0:
                print(f"[EXP001] written={written}")

    content_hash = hash_file(artifact_path)
    uri = (
        f"artifacts/{ARTIFACT_ID}/feature_results.jsonl"
    )
    from strategies.paaf.evidence.models import ArtifactReference

    artifact_ref = ArtifactReference(
        artifact_id=ARTIFACT_ID,
        uri=uri,
        content_hash=content_hash,
        artifact_type="feature_results",
    )

    context = ExperimentContext(
        experiment_id=EXPERIMENT_ID,
        sensor_id=SENSOR_ID,
        sensor_version=SENSOR_VERSION,
        parameters=parameters,
        hypothesis=HYPOTHESIS,
        code_revision=code_revision,
        data_fingerprint=data_fingerprint,
        environment_fingerprint=environment_fingerprint,
        subject_kind="feature_sensor",
        data_protocol_version="docs/07_DATA_SPEC.md@1.0.0",
    )
    repository = EvidenceRepository(
        root_path=ROOT / "research" / "output" / "evidence",
    )
    workflow = ExperimentWorkflow(repository)
    manifest = workflow.build_manifest(context, artifact_refs=(artifact_ref,))
    workflow.persist_manifest(manifest)

    created_at = datetime.now(tz=timezone.utc)
    run_metadata = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "created_at": created_at.isoformat(),
        "authorization": "Feature Artifact only",
        "evaluation_authorized": False,
        "evidence_authorized": False,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "period_start": PERIOD_START.date().isoformat(),
        "period_end": PERIOD_END.date().isoformat(),
        "bars_in_period": int(period_mask.sum()),
        "feature_rows_written": written,
        "ready_atr_ratio": ready_n,
        "null_atr_ratio": null_n,
        "rollover_flag_true": rollover_n,
        "code_revision": code_revision,
        "data_fingerprint": data_fingerprint,
        "environment_fingerprint": environment_fingerprint,
        "parameter_fingerprint": manifest.parameter_fingerprint,
        "artifact": artifact_ref.to_dict(),
        "dataset_fingerprint_payload": dataset_payload,
        "period_first_bar": str(period_frame["dt_cst"].iloc[0]),
        "period_last_bar": str(period_frame["dt_cst"].iloc[-1]),
        "used_yymms": sorted(used_yymms),
    }
    with run_meta_path.open("x", encoding="utf-8", newline="\n") as meta:
        meta.write(f"{canonical_json_dumps(run_metadata)}\n")

    print("[EXP001] complete")
    print(f"  experiment_id={EXPERIMENT_ID}")
    print(f"  run_id={RUN_ID}")
    print(f"  rows={written} ready={ready_n} null={null_n} rollover={rollover_n}")
    print(f"  artifact={artifact_path.relative_to(ROOT)}")
    print(f"  content_hash={content_hash}")
    print(f"  data_fingerprint={data_fingerprint}")
    print(f"  code_revision={code_revision}")
    print("  evaluation=NOT RUN")
    print("  evidence=NOT RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
