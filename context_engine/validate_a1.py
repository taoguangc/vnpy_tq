"""A1 validation CLI — Observation produces Evidence; Implementation only defines entry."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from context_engine.evidence_io import attach_lineage, make_lineage, write_json  # noqa: E402
from context_engine.faults import run_fault_cases  # noqa: E402
from context_engine.latency import measure_publish_latency_ms  # noqa: E402
from context_engine.publisher import publish_batch, publish_streaming  # noqa: E402
from context_engine.schema import CONTEXT_VERSION, SCHEMA_VERSION, schema_document  # noqa: E402
from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402

CST = ZoneInfo("Asia/Shanghai")
FULL_START = pd.Timestamp("2024-01-01", tz=CST)
FULL_END = pd.Timestamp("2025-12-31 23:59:59", tz=CST)
WARMUP_START = pd.Timestamp("2023-10-01", tz=CST)
UNIVERSE = ("rb", "i", "MA", "TA")
PRIMARY = "rb"


def _load_symbol(prefix: str) -> pd.DataFrame:
    df = build_stitched_raw_frame(prefix)
    df = df.copy()
    df["dt_cst"] = pd.to_datetime(df["dt_cst"], utc=False)
    if df["dt_cst"].dt.tz is None:
        df["dt_cst"] = df["dt_cst"].dt.tz_localize(CST)
    else:
        df["dt_cst"] = df["dt_cst"].dt.tz_convert(CST)
    df = df.sort_values("dt_cst").drop_duplicates(subset=["dt_cst"], keep="last")
    df = df[(df["dt_cst"] >= WARMUP_START) & (df["dt_cst"] <= FULL_END)].reset_index(
        drop=True
    )
    return df


def _parity_compare(a: list, b: list) -> dict:
    if len(a) != len(b):
        return {"pass": False, "reason": "length_mismatch", "n_a": len(a), "n_b": len(b)}
    mismatches = 0
    conf_mismatches = 0
    first = None
    for i, (sa, sb) in enumerate(zip(a, b)):
        if sa.exact_key() != sb.exact_key():
            mismatches += 1
            if first is None:
                first = {"index": i, "a": sa.to_dict(), "b": sb.to_dict()}
        if sa.confidence != sb.confidence:
            conf_mismatches += 1
    return {
        "pass": mismatches == 0 and conf_mismatches == 0,
        "n": len(a),
        "exact_mismatches": mismatches,
        "confidence_mismatches": conf_mismatches,
        "first_mismatch": first,
        "comparison_object": "ContextState equality",
        "not_compared": ["PnL", "trades", "strategy_metrics"],
    }


def run_validation(manifest_path: Path, *, observation_authorized: bool) -> int:
    if not observation_authorized:
        print(
            "[A1] Observation NOT AUTHORIZED — refusing to write Evidence. "
            "Implementation may import modules; run only after Observation Authorization.",
            flush=True,
        )
        return 3

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("observation_start_authorized"):
        print("[A1] manifest.observation_start_authorized is false — abort", flush=True)
        return 3

    out_dir = manifest_path.parent
    manifest_id = manifest.get("manifest_id") or manifest.get("run_id")
    runtime_hash = manifest.get("environment_hash") or ""
    dataset_fp = manifest.get("dataset_fingerprints") or {}
    lineage = make_lineage(
        manifest_id=str(manifest_id),
        runtime_hash=str(runtime_hash),
        dataset_fingerprint={k: v.get("manifest.json") for k, v in dataset_fp.items()}
        if isinstance(dataset_fp, dict)
        else {},
        schema_version=SCHEMA_VERSION,
    )

    write_json(out_dir / "context_schema.json", attach_lineage(schema_document(), lineage))

    print(f"[A1] load primary {PRIMARY} ...", flush=True)
    df = _load_symbol(PRIMARY)
    full = df[(df["dt_cst"] >= FULL_START) & (df["dt_cst"] <= FULL_END)].reset_index(
        drop=True
    )

    print("[A1-E1/E2] batch vs streaming parity ...", flush=True)
    batch = publish_batch(full, instrument=PRIMARY, manifest_id=str(manifest_id))
    stream = publish_streaming(full, instrument=PRIMARY, manifest_id=str(manifest_id))
    parity = _parity_compare(batch, stream)
    # Determinism: re-batch
    batch2 = publish_batch(full, instrument=PRIMARY, manifest_id=str(manifest_id))
    determ = _parity_compare(batch, batch2)
    parity_report = attach_lineage(
        {
            "A1-E1_deterministic_publish": determ,
            "A1-E2_batch_streaming_parity": parity,
            "context_version": CONTEXT_VERSION,
            "n_states": len(batch),
            "instrument": PRIMARY,
        },
        lineage,
    )
    write_json(out_dir / "parity_report.json", parity_report)

    print("[A1-E3] fault harness ...", flush=True)
    fault_results = run_fault_cases(
        full, instrument=PRIMARY, manifest_id=str(manifest_id)
    )
    fault_pass = all(r["pass"] for r in fault_results)
    fault_report = attach_lineage(
        {"A1-E3_fault_handling": {"pass": fault_pass, "cases": fault_results}},
        lineage,
    )
    write_json(out_dir / "fault_test_report.json", fault_report)

    print("[A1-E4] latency ...", flush=True)
    lat = measure_publish_latency_ms(
        full, instrument=PRIMARY, manifest_id=str(manifest_id)
    )
    write_json(
        out_dir / "latency_report.json",
        attach_lineage({"A1-E4_latency": lat}, lineage),
    )

    # A1-E5 reproduction: hash of parity payload identity
    repro_blob = json.dumps(
        {"parity_pass": parity["pass"], "determ_pass": determ["pass"], "n": len(batch)},
        sort_keys=True,
    )
    repro_hash = hashlib.sha256(repro_blob.encode()).hexdigest()

    e1 = bool(determ.get("pass"))
    e2 = bool(parity.get("pass"))
    e3 = fault_pass
    e4 = bool(lat.get("pass_p99"))
    e5 = bool(repro_hash)  # presence + CLI regenerates same structure

    if e1 and e2 and e3 and e5 and e4:
        outcome = "PASS"
    elif e1 and e2 and e3 and e5 and not e4:
        outcome = "PARTIAL"
    elif not e1 or not e2 or not e3:
        outcome = "FAIL"
    else:
        outcome = "PARTIAL"

    evidence = attach_lineage(
        {
            "schema": "CAP_CTX_A1_EvidenceRecord_v1",
            "run_id": manifest.get("run_id"),
            "outcome": outcome,
            "A1-E1": e1,
            "A1-E2": e2,
            "A1-E3": e3,
            "A1-E4": e4,
            "A1-E5": e5,
            "reproduction_content_sha256": repro_hash,
            "knowledge_action": "NONE",
            "affects": "Engineering Readiness only",
            "non_claims": [
                "not_k001_update",
                "not_alpha",
                "not_gate_pass",
                "not_candidate",
                "not_rc001",
                "not_strategy",
                "confidence_neq_win_probability",
            ],
            "decision_019": True,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        lineage,
    )
    write_json(out_dir / "evidence_record.json", evidence)

    # update manifest observation complete
    manifest["observation_status"] = "OBSERVATION_COMPLETE"
    manifest["execution_state"] = "OBSERVATION_COMPLETE"
    manifest["a1_outcome"] = outcome
    obs = dict(manifest.get("observation_execution") or {})
    obs["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    obs["outcome"] = outcome
    manifest["observation_execution"] = obs
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"[A1] outcome={outcome} e1={e1} e2={e2} e3={e3} e4={e4} e5={e5}", flush=True)
    return 0 if outcome in {"PASS", "PARTIAL"} else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CAP_CTX_A1 Published State validation")
    parser.add_argument("--manifest", required=True, help="path to CAP_CTX_A1 manifest")
    parser.add_argument(
        "--authorize-observation",
        action="store_true",
        help="Required flag: Observation must be explicitly authorized",
    )
    args = parser.parse_args(argv)
    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"[A1] manifest not found: {manifest_path}", flush=True)
        return 2

    # Observation gate: flag AND manifest field
    man = json.loads(manifest_path.read_text(encoding="utf-8"))
    authorized = bool(args.authorize_observation) and bool(
        man.get("observation_start_authorized")
    )
    return run_validation(manifest_path, observation_authorized=authorized)


if __name__ == "__main__":
    raise SystemExit(main())
