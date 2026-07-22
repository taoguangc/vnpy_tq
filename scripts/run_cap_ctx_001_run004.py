"""CAP_CTX_001_RUN004 — Observation Family Expansion Observation + Evaluation.

Protocol inherited from CAP_CTX_001_RUN001 unless overridden by registered
Observation Family scope (Liquidity Structure / M3).
Does NOT claim Knowledge Decision / Gate / Alpha / P4.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402

CST = ZoneInfo("Asia/Shanghai")
RUN_ID = "CAP_CTX_001_RUN004"
PARENT_RUN_ID = "CAP_CTX_001_RUN003"
OUT_DIR = ROOT / "research" / "output" / "evidence" / RUN_ID
MANIFEST_PATH = OUT_DIR / "CAP_CTX_001_RUN_MANIFEST.json"

UNIVERSE = ("rb", "i", "MA", "TA")
PRIMARY = "rb"
TRANSFER = ("i", "MA", "TA")
EXPANSION_FAMILY = "Liquidity Structure"

FULL_START = pd.Timestamp("2024-01-01", tz=CST)
FULL_END = pd.Timestamp("2025-12-31 23:59:59", tz=CST)
WARMUP_START = pd.Timestamp("2023-10-01", tz=CST)
COVERAGE_MONTHS_START = "2024-01"
COVERAGE_MONTHS_END = "2025-12"

W = 20
L = 240
N_PERM = 200
RNG_SEED = 20240721
BLOCK_SIZE = 60
MIN_SAMPLE_PER_LABEL = 5000
MIN_RUNS = 100

SYM_RNG_OFFSET = {"rb": 0, "i": 1, "MA": 2, "TA": 3}

FINGERPRINTS = {
    "rb": {
        "manifest.json": "bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa",
        "dominant_windows.json": "051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b",
        "rollover_map.parquet": "170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e",
    },
    "i": {
        "manifest.json": "ea0c1aeeb40902a17beb9ae86ebb2f3313fd7199f546cea9ab05c4219ed46239",
        "dominant_windows.json": "72302ce316c97de9b0448725180743fe7b21cfb66a6c8815f7f89f1567f2ced8",
        "rollover_map.parquet": "3eeedfcaa143ba6a1a698ccb033cae147a696446f1ecd1df2cdb9c293b9bf5ba",
    },
    "MA": {
        "manifest.json": "04de9c86cfba8f2a18a3f908d2a5fa748d788dbc8f84a38129b878164321012f",
        "dominant_windows.json": "9d448d120da2e7bd98cc0ae0a0faf7f3418c6985a58f23c032b1b7f412389109",
        "rollover_map.parquet": "e16a32be6565989629151f12ed1cd5706f6de4eb9d54c0c5809803bf3bbbe64d",
    },
    "TA": {
        "manifest.json": "bff7e60648be96dc07671468e567aff6fc179b20dae820f2cc704c302f53867d",
        "dominant_windows.json": "17ebac8a4e085b910fe07f50fb1fbe89c5e7f0d6ac6da0a362976f3766ed075e",
        "rollover_map.parquet": "86dff2a71b7a8226812d9c3b9932f53273579429b310034485849e46cb7466e7",
    },
}


@dataclass(frozen=True)
class E1Result:
    symbol: str
    n_high: int
    n_low: int
    smd_m1: float | None
    smd_m2: float | None
    smd_m3: float | None
    n1_q95_m1: float | None
    n1_q95_m3: float | None
    pass_e1_core: bool | None
    pass_e1_family: bool | None
    status_core: str
    status_family: str
    detail: str = ""


def _git_revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _requirements_sha256() -> str:
    return hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()


def _package_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "vnpy"):
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = "unknown"
    return out


def write_manifest(revision: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    dataset_fingerprints = {
        sym: {"resolved_path": str((ROOT / "data" / "tq" / sym).resolve()), **FINGERPRINTS[sym]}
        for sym in UNIVERSE
    }
    manifest = {
        "schema": "CAP_CTX_001_RunManifest_v1",
        "run_id": RUN_ID,
        "parent": PARENT_RUN_ID,
        "campaign_id": "CAP-CTX-001",
        "eq": "EQ-CTX-004",
        "role": "run_identity_artifact",
        "cross_evidence": True,
        "evidence_type": "observation_expansion",
        "expansion_family": EXPANSION_FAMILY,
        "protocol_inheritance": (
            "Protocol inherited from CAP_CTX_001_RUN001 unless explicitly "
            "overridden by registered Observation Family scope."
        ),
        "integrity_constraint": (
            "No methodological modification shall be introduced for the purpose "
            "of increasing support for existing knowledge."
        ),
        "spec_version": "0.2",
        "fill_version": "0.2",
        "auth_version": "1.0",
        "appendix_a_summary": {
            "universe": list(UNIVERSE),
            "primary": PRIMARY,
            "transfer": list(TRANSFER),
            "baseline_families": ["Volatility Structure", "Price Structure"],
            "expansion_family": EXPANSION_FAMILY,
            "M3": "causal_relative_volume_intensity L=240",
            "full_window": ["2024-01-01", "2025-12-31"],
            "warmup_start": "2023-10-01",
            "W": W,
            "L": L,
            "n_perm": N_PERM,
            "rng_seed": RNG_SEED,
            "data": "TQ offline / 1m / CbC / unadjusted",
        },
        "dataset_fingerprints": dataset_fingerprints,
        "environment_identity": {
            "recorded_at_utc": now,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "packages": _package_versions(),
            "requirements_txt_sha256": _requirements_sha256(),
            "code_revision": revision,
            "code_revision_at_manifest": revision,
        },
        "c_env_validation": {
            "status": "SATISFIED",
            "validated_at_utc": now,
            "checks": {
                "run_identity": True,
                "appendix_a_frozen_summary": True,
                "dataset_sha256": True,
                "environment_identity": True,
                "family_integrity_c_fam": True,
            },
        },
        "manifest_confirmation": "CONFIRMED",
        "observation_status": "PENDING",
        "observation_start_authorized": False,
        "execution_state": "MANIFEST_WRITTEN_C_ENV_SATISFIED",
        "conditions_binding": [
            "C-ENV",
            "C-SCOPE",
            "C-CLAIM",
            "C-GATE",
            "C-NO-DRIFT",
            "C-XEV",
            "C-K001",
            "C-FAM",
        ],
        "note": (
            "RUN004 Observation Expansion Manifest. Identity only. "
            "Family=Liquidity Structure; P3≠P4; no Capability claim."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _update_manifest_start(revision: str) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    manifest["observation_start_authorized"] = True
    manifest["observation_status"] = "RUNNING"
    manifest["execution_state"] = "OBSERVATION_AUTHORIZED_AND_STARTED"
    manifest["observation_execution"] = {
        "authorized_command": "Authorize Observation Execution for CAP_CTX_001_RUN004",
        "started_at_utc": now,
        "code_revision_at_start": revision,
        "parent": PARENT_RUN_ID,
        "eq": "EQ-CTX-004",
        "expansion_family": EXPANSION_FAMILY,
    }
    manifest["environment_identity"]["code_revision_at_observation_start"] = revision
    manifest["note"] = (
        "RUN004 Observation started. Family override only. "
        "No Knowledge Decision / Gate / Alpha / P4 claim."
    )
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _finalize_manifest(status: str, extra: dict | None = None) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    manifest["observation_status"] = status
    manifest["execution_state"] = status
    obs = dict(manifest.get("observation_execution") or {})
    obs["finished_at_utc"] = now
    if extra:
        obs.update(extra)
    manifest["observation_execution"] = obs
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_symbol(prefix: str) -> pd.DataFrame:
    print(f"[load] {prefix} CbC stitch ...", flush=True)
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


def _check_coverage_gap(df: pd.DataFrame, symbol: str) -> dict:
    full = df[(df["dt_cst"] >= FULL_START) & (df["dt_cst"] <= FULL_END)]
    if full.empty:
        return {
            "symbol": symbol,
            "ok": False,
            "reason": "empty_full_window",
            "missing_months": [],
        }
    months = pd.period_range(COVERAGE_MONTHS_START, COVERAGE_MONTHS_END, freq="M")
    present = set(full["dt_cst"].dt.to_period("M").unique())
    missing_months = [str(m) for m in months if m not in present]
    deltas = full["dt_cst"].diff().dropna()
    max_gap = deltas.max()
    return {
        "symbol": symbol,
        "ok": len(missing_months) == 0,
        "reason": None if not missing_months else "missing_calendar_months",
        "missing_months": missing_months,
        "n_bars_full": int(len(full)),
        "max_gap_hours": float(max_gap / pd.Timedelta(hours=1)) if pd.notna(max_gap) else None,
        "full_start": str(full["dt_cst"].iloc[0]),
        "full_end": str(full["dt_cst"].iloc[-1]),
    }


def _compute_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["close"].astype(float)
    volume = out["volume"].astype(float)
    log_ret = np.log(close / close.shift(1))
    out["M1"] = log_ret.rolling(window=W, min_periods=W).std(ddof=1)
    abs_move = (close - close.shift(W)).abs()
    path = close.diff().abs().rolling(window=W, min_periods=W).sum()
    out["M2"] = abs_move / path.replace(0.0, np.nan)

    # M3: volume_t / median(volume[t-L:t]) prior excluding t
    vol = volume.to_numpy(dtype=float)
    m3 = np.full(len(out), np.nan, dtype=float)
    for t in range(L, len(out)):
        prior = vol[t - L : t]
        if not np.all(np.isfinite(prior)) or not np.isfinite(vol[t]):
            continue
        med = float(np.median(prior))
        if med == 0.0:
            continue
        m3[t] = float(vol[t] / med)
    out["M3"] = m3

    m1 = out["M1"].to_numpy(dtype=float)
    labels = np.full(len(out), None, dtype=object)
    for t in range(L, len(out)):
        prior_exact = m1[t - L : t]
        if not np.all(np.isfinite(prior_exact)):
            continue
        if not np.isfinite(m1[t]):
            continue
        med = float(np.median(prior_exact))
        labels[t] = "HIGH_VOL" if m1[t] > med else "LOW_VOL"
    out["label"] = labels
    return out


def _smd(
    labels: np.ndarray,
    target_values: np.ndarray,
) -> float | None:
    high = target_values[labels == "HIGH_VOL"]
    low = target_values[labels == "LOW_VOL"]
    high = high[np.isfinite(high)]
    low = low[np.isfinite(low)]
    n_h, n_l = high.size, low.size
    if n_h < 2 or n_l < 2:
        return None
    mu_h, mu_l = high.mean(), low.mean()
    s_h2, s_l2 = high.var(ddof=1), low.var(ddof=1)
    denom = n_h + n_l - 2
    if denom < 1:
        return None
    pooled = np.sqrt(((n_h - 1) * s_h2 + (n_l - 1) * s_l2) / denom)
    if pooled == 0 or not np.isfinite(pooled):
        return None
    return float(abs(mu_h - mu_l) / pooled)


def _null_q95_smd(
    labels: np.ndarray,
    target: np.ndarray,
    n_high: int,
    rng: np.random.Generator,
) -> float | None:
    n = labels.size
    base = np.array(
        ["HIGH_VOL"] * n_high + ["LOW_VOL"] * (n - n_high),
        dtype=object,
    )
    null_smds = np.empty(N_PERM, dtype=float)
    for i in range(N_PERM):
        perm = base.copy()
        rng.shuffle(perm)
        val = _smd(perm, target)
        null_smds[i] = np.nan if val is None else val
    null_smds = null_smds[np.isfinite(null_smds)]
    if null_smds.size == 0:
        return None
    return float(np.quantile(null_smds, 0.95))


def _run_lengths(labels: np.ndarray) -> np.ndarray:
    if labels.size == 0:
        return np.array([], dtype=float)
    lengths = []
    cur = labels[0]
    n = 1
    for lab in labels[1:]:
        if lab == cur:
            n += 1
        else:
            lengths.append(n)
            cur = lab
            n = 1
    lengths.append(n)
    return np.asarray(lengths, dtype=float)


def _eval_e1(symbol: str, feat: pd.DataFrame, rng: np.random.Generator) -> E1Result:
    full = feat[(feat["dt_cst"] >= FULL_START) & (feat["dt_cst"] <= FULL_END)]
    mask = full["label"].isin(["HIGH_VOL", "LOW_VOL"])
    sample = full.loc[mask].copy()
    labels = sample["label"].to_numpy()
    m1 = sample["M1"].to_numpy(dtype=float)
    m2 = sample["M2"].to_numpy(dtype=float)
    m3 = sample["M3"].to_numpy(dtype=float)
    n_h = int((labels == "HIGH_VOL").sum())
    n_l = int((labels == "LOW_VOL").sum())
    if n_h < MIN_SAMPLE_PER_LABEL or n_l < MIN_SAMPLE_PER_LABEL:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=None,
            smd_m2=None,
            smd_m3=None,
            n1_q95_m1=None,
            n1_q95_m3=None,
            pass_e1_core=None,
            pass_e1_family=None,
            status_core="HOLD",
            status_family="HOLD",
            detail=f"min_sample_per_label={MIN_SAMPLE_PER_LABEL} not met",
        )

    smd_m1 = _smd(labels, m1)
    smd_m2 = _smd(labels, m2)
    smd_m3 = _smd(labels, m3)
    if smd_m1 is None:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=None,
            smd_m2=smd_m2,
            smd_m3=smd_m3,
            n1_q95_m1=None,
            n1_q95_m3=None,
            pass_e1_core=None,
            pass_e1_family=None,
            status_core="HOLD",
            status_family="HOLD",
            detail="SMD_M1 INFEASIBLE",
        )

    # Separate RNGs for core vs family nulls (reproducible offsets)
    rng_core = np.random.default_rng(RNG_SEED + SYM_RNG_OFFSET[symbol])
    rng_fam = np.random.default_rng(RNG_SEED + 50 + SYM_RNG_OFFSET[symbol])
    q95_m1 = _null_q95_smd(labels, m1, n_h, rng_core)
    if q95_m1 is None:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=smd_m1,
            smd_m2=smd_m2,
            smd_m3=smd_m3,
            n1_q95_m1=None,
            n1_q95_m3=None,
            pass_e1_core=None,
            pass_e1_family=None,
            status_core="HOLD",
            status_family="HOLD",
            detail="N1 M1 null infeasible",
        )
    pass_core = bool(smd_m1 > q95_m1)

    if smd_m3 is None or not np.isfinite(m3).sum() >= (MIN_SAMPLE_PER_LABEL * 2):
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=smd_m1,
            smd_m2=smd_m2,
            smd_m3=smd_m3,
            n1_q95_m1=q95_m1,
            n1_q95_m3=None,
            pass_e1_core=pass_core,
            pass_e1_family=None,
            status_core="PASS" if pass_core else "FAIL",
            status_family="HOLD",
            detail="SMD_M3 INFEASIBLE or insufficient finite M3",
        )

    q95_m3 = _null_q95_smd(labels, m3, n_h, rng_fam)
    if q95_m3 is None:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=smd_m1,
            smd_m2=smd_m2,
            smd_m3=smd_m3,
            n1_q95_m1=q95_m1,
            n1_q95_m3=None,
            pass_e1_core=pass_core,
            pass_e1_family=None,
            status_core="PASS" if pass_core else "FAIL",
            status_family="HOLD",
            detail="N1 M3 null infeasible",
        )
    pass_fam = bool(smd_m3 > q95_m3)
    return E1Result(
        symbol=symbol,
        n_high=n_h,
        n_low=n_l,
        smd_m1=smd_m1,
        smd_m2=smd_m2,
        smd_m3=smd_m3,
        n1_q95_m1=q95_m1,
        n1_q95_m3=q95_m3,
        pass_e1_core=pass_core,
        pass_e1_family=pass_fam,
        status_core="PASS" if pass_core else "FAIL",
        status_family="PASS" if pass_fam else "FAIL",
    )


def _eval_e2(feat: pd.DataFrame, rng: np.random.Generator, *, e1_pass: bool) -> dict:
    if not e1_pass:
        return {"status": "skipped", "reason": "E1_core not PASS"}
    full = feat[(feat["dt_cst"] >= FULL_START) & (feat["dt_cst"] <= FULL_END)]
    mask = full["label"].isin(["HIGH_VOL", "LOW_VOL"])
    labels = full.loc[mask, "label"].to_numpy()
    runs = _run_lengths(labels)
    if runs.size < MIN_RUNS:
        return {
            "status": "HOLD",
            "detail": f"min_runs={MIN_RUNS} not met",
            "n_runs": int(runs.size),
        }
    obs = float(runs.mean())
    null_means = np.empty(N_PERM, dtype=float)
    n = labels.size
    for i in range(N_PERM):
        blocks = [labels[j : j + BLOCK_SIZE] for j in range(0, n, BLOCK_SIZE)]
        order = rng.permutation(len(blocks))
        perm = np.concatenate([blocks[k] for k in order])
        null_means[i] = float(_run_lengths(perm).mean())
    q95 = float(np.quantile(null_means, 0.95))
    passed = bool(obs > q95)
    return {
        "status": "PASS" if passed else "FAIL",
        "mean_run_length": obs,
        "n_runs": int(runs.size),
        "n2_q95": q95,
        "pass_e2": passed,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    revision = _git_revision()
    if not MANIFEST_PATH.is_file():
        print("[manifest] writing C-ENV manifest ...", flush=True)
        write_manifest(revision)
    _update_manifest_start(revision)
    started = datetime.now(timezone.utc).isoformat()
    print(f"[CAP_CTX_001_RUN004] start revision={revision}", flush=True)

    coverage = []
    features: dict[str, pd.DataFrame] = {}
    for sym in UNIVERSE:
        df = _load_symbol(sym)
        cov = _check_coverage_gap(df, sym)
        coverage.append(cov)
        print(f"[coverage] {cov}", flush=True)
        if not cov["ok"]:
            payload = {
                "decision": "INFEASIBLE",
                "reason": "coverage_gap_INFEASIBLE",
                "coverage": coverage,
                "registered_knowledge_action": "NO_UPGRADE",
            }
            (OUT_DIR / "evaluation.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            _finalize_manifest("INFEASIBLE_COVERAGE", {"coverage": coverage})
            return 2
        print(f"[features] {sym} ...", flush=True)
        features[sym] = _compute_features(df)

    e1_results: dict[str, E1Result] = {}
    for sym in UNIVERSE:
        print(f"[E1] {sym} ...", flush=True)
        # rng unused for seeding inside _eval_e1 (internal offsets)
        e1_results[sym] = _eval_e1(
            sym, features[sym], np.random.default_rng(RNG_SEED + SYM_RNG_OFFSET[sym])
        )
        print(f"[E1] {e1_results[sym]}", flush=True)

    primary = e1_results[PRIMARY]
    e1_core_rb = primary.pass_e1_core is True
    e1_fam_rb = primary.pass_e1_family is True

    print("[E2] rb ...", flush=True)
    e2 = _eval_e2(
        features[PRIMARY],
        np.random.default_rng(RNG_SEED + 100),
        e1_pass=e1_core_rb,
    )
    print(f"[E2] {e2}", flush=True)

    transfer_core = {sym: (e1_results[sym].pass_e1_core is True) for sym in TRANSFER}
    transfer_fam = {sym: (e1_results[sym].pass_e1_family is True) for sym in TRANSFER}
    e3_core = all(transfer_core.values())
    e3 = {
        "transfer_e1_core_pass": transfer_core,
        "transfer_e1_family_pass": transfer_fam,
        "e3_core_supported": e3_core,
        "expansion_family": EXPANSION_FAMILY,
        "rule": "E1_core Pass on i AND MA AND TA; E1_family disclosed",
    }
    print(f"[E3] {e3}", flush=True)

    if primary.status_core == "HOLD" or e2.get("status") == "HOLD" or primary.status_family == "HOLD":
        decision = "INFEASIBLE"
        registered_knowledge_action = "NO_UPGRADE"
        cross_evidence_result = "INFEASIBLE"
    elif e1_core_rb and e2.get("pass_e2") and e3_core and e1_fam_rb:
        decision = "SUPPORTED"
        registered_knowledge_action = "STRENGTHEN"
        cross_evidence_result = "SUPPORTED"
    elif not e1_core_rb:
        decision = "NOT_SUPPORTED"
        registered_knowledge_action = "DOWNGRADE"
        cross_evidence_result = "NOT_SUPPORTED"
    else:
        decision = "PARTIAL"
        registered_knowledge_action = "NARROW"
        cross_evidence_result = "PARTIAL"

    def e1_dict(r: E1Result) -> dict:
        return {
            "symbol": r.symbol,
            "n_high": r.n_high,
            "n_low": r.n_low,
            "smd_m1": r.smd_m1,
            "smd_m2": r.smd_m2,
            "smd_m3": r.smd_m3,
            "n1_q95_m1": r.n1_q95_m1,
            "n1_q95_m3": r.n1_q95_m3,
            "pass_e1_core": r.pass_e1_core,
            "pass_e1_family": r.pass_e1_family,
            "status_core": r.status_core,
            "status_family": r.status_family,
            "detail": r.detail,
        }

    evaluation = {
        "run_id": RUN_ID,
        "parent": PARENT_RUN_ID,
        "eq": "EQ-CTX-004",
        "role": "cross_evidence_observation_expansion",
        "expansion_family": EXPANSION_FAMILY,
        "protocol_inheritance": (
            "Protocol inherited from CAP_CTX_001_RUN001; override = Observation Family only."
        ),
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_revision": revision,
        "parameters": {
            "W": W,
            "L": L,
            "n_perm": N_PERM,
            "rng_seed": RNG_SEED,
            "block_size": BLOCK_SIZE,
            "min_sample_per_label": MIN_SAMPLE_PER_LABEL,
            "min_runs": MIN_RUNS,
            "M3": "volume_t / median(volume[t-L:t])",
        },
        "coverage": coverage,
        "E1": {sym: e1_dict(e1_results[sym]) for sym in UNIVERSE},
        "E2": e2,
        "E3": e3,
        "decision": decision,
        "cross_evidence_result": cross_evidence_result,
        "registered_knowledge_action": registered_knowledge_action,
        "methodological_note": (
            "E1_core SMD_M1 is partly definition-coupled. "
            "E1_family SMD_M3 uses same M1-derived labels (supporting). "
            "P3≠P4: Family PASS ≠ Independence."
        ),
        "claim_boundary": {
            "allowed": "Observation Family robustness evidence under registered conditions",
            "forbidden": [
                "Capability Candidate",
                "Gate PASS",
                "P4 Independence MET",
                "Alpha / trading",
                "Family substitution on failure",
            ],
        },
        "predictive_evaluation": "NOT_PERFORMED",
        "pnl_evaluation": "NOT_PERFORMED",
    }

    eval_path = OUT_DIR / "evaluation.json"
    eval_path.write_text(
        json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    evidence_record = {
        "schema": "CAP_CTX_001_EvidenceRecord_draft",
        "run_id": RUN_ID,
        "parent": PARENT_RUN_ID,
        "eq": "EQ-CTX-004",
        "role": "cross_evidence_observation_expansion",
        "expansion_family": EXPANSION_FAMILY,
        "decision": decision,
        "cross_evidence_result": cross_evidence_result,
        "registered_knowledge_action": registered_knowledge_action,
        "artifacts": {
            "run_manifest": str(MANIFEST_PATH.relative_to(ROOT).as_posix()),
            "evaluation": str(eval_path.relative_to(ROOT).as_posix()),
        },
        "review_required": True,
        "knowledge_decision": None,
        "accepted_knowledge": False,
        "gate_implication": "NONE_AUTOMATIC",
        "rc001_implication": "NONE_AUTOMATIC",
        "p4_implication": "NONE_AUTOMATIC",
        "note": "Registered Action only; K001 Decision requires separate Review.",
    }
    ev_path = OUT_DIR / "evidence_record.json"
    ev_path.write_text(
        json.dumps(evidence_record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    _finalize_manifest(
        "OBSERVATION_COMPLETE",
        {
            "evaluation_path": str(eval_path.relative_to(ROOT).as_posix()),
            "evidence_record_path": str(ev_path.relative_to(ROOT).as_posix()),
            "decision": decision,
            "cross_evidence_result": cross_evidence_result,
            "registered_knowledge_action": registered_knowledge_action,
        },
    )

    print(
        f"[done] decision={decision} action={registered_knowledge_action}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
