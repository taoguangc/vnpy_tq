"""CAP_CTX_001_L1_RUN001 — Independence Repair Observation + Evaluation.

GEN-L1-v0.2 (Price/M2 labels) ≠ LER-CTX-L1 v0.2 (SMD_FWD_ABSRET / persistence / transfer).
Does NOT claim Knowledge Decision / Gate / Capability / Strategy / Alpha.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402

CST = ZoneInfo("Asia/Shanghai")
RUN_ID = "CAP_CTX_001_L1_RUN001"
OUT_DIR = ROOT / "research" / "output" / "evidence" / RUN_ID
MANIFEST_PATH = OUT_DIR / "CAP_CTX_001_L1_RUN_MANIFEST.json"
LER_PATH = OUT_DIR / "LER_CTX_L1_SEALED.json"

UNIVERSE = ("rb", "i", "MA", "TA")
PRIMARY = "rb"
TRANSFER = ("i", "MA", "TA")

FULL_START = pd.Timestamp("2024-01-01", tz=CST)
FULL_END = pd.Timestamp("2025-12-31 23:59:59", tz=CST)
WARMUP_START = pd.Timestamp("2023-10-01", tz=CST)
COVERAGE_MONTHS_START = "2024-01"
COVERAGE_MONTHS_END = "2025-12"

W = 20
L = 240
H = 20
N_PERM = 200
RNG_SEED = 20240721
MIN_SAMPLE_PER_LABEL = 5000
MIN_RUNS = 100

HIGH = "HIGH_EFF"
LOW = "LOW_EFF"
SYM_RNG_OFFSET = {"rb": 0, "i": 1, "MA": 2, "TA": 3}

AUTH_COMMAND = "Authorize Observation Execution for CAP_CTX_001_L1_RUN001"


@dataclass(frozen=True)
class E1Result:
    symbol: str
    n_high: int
    n_low: int
    smd_fwd: float | None
    n1_q95: float | None
    smd_m2_diagnostic: float | None
    pass_e1: bool | None
    status: str
    detail: str = ""


def _git_revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _verify_ler_seal() -> str:
    if not LER_PATH.is_file():
        raise FileNotFoundError(f"LER sealed artifact missing: {LER_PATH}")
    ler = json.loads(LER_PATH.read_text(encoding="utf-8"))
    if ler.get("seal_status") != "SEALED":
        raise RuntimeError("LER not SEALED")
    stored = ler.get("content_sha256")
    body = {k: v for k, v in ler.items() if k != "content_sha256"}
    canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if stored != digest:
        raise RuntimeError(f"LER hash mismatch stored={stored} computed={digest}")
    return digest


def _update_manifest_start(revision: str, ler_hash: str) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    manifest["observation_start_authorized"] = True
    manifest["observation_status"] = "RUNNING"
    manifest["execution_state"] = "OBSERVATION_AUTHORIZED_AND_STARTED"
    manifest["observation_execution"] = {
        "authorized_command": AUTH_COMMAND,
        "started_at_utc": now,
        "code_revision_at_start": revision,
        "ler_content_sha256_verified": ler_hash,
        "gen_recipe": "GEN-L1-v0.2",
        "ler_version": "LER-CTX-L1 v0.2",
    }
    manifest["environment_identity"]["code_revision_at_observation_start"] = revision
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
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
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
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


def _check_coverage(df: pd.DataFrame, symbol: str) -> dict:
    full = df[(df["dt_cst"] >= FULL_START) & (df["dt_cst"] <= FULL_END)]
    if full.empty:
        return {"symbol": symbol, "ok": False, "reason": "empty_full_window"}
    months = pd.period_range(COVERAGE_MONTHS_START, COVERAGE_MONTHS_END, freq="M")
    present = set(full["dt_cst"].dt.to_period("M").unique())
    missing = [str(m) for m in months if m not in present]
    return {
        "symbol": symbol,
        "ok": len(missing) == 0,
        "missing_months": missing,
        "n_bars_full": int(len(full)),
        "full_start": str(full["dt_cst"].iloc[0]),
        "full_end": str(full["dt_cst"].iloc[-1]),
    }


def _compute_gen_features(df: pd.DataFrame) -> pd.DataFrame:
    """GEN-L1-v0.2: M2 labels; F_t forward abs-return mean (evaluation object)."""
    out = df.copy()
    close = out["close"].astype(float)
    log_ret = np.log(close / close.shift(1))
    abs_log_ret = log_ret.abs()

    abs_move = (close - close.shift(W)).abs()
    path = close.diff().abs().rolling(window=W, min_periods=W).sum()
    out["M2"] = abs_move / path.replace(0.0, np.nan)

    # Causal rolling median of prior L bars (exclude t): rolling(L).median().shift(1)
    med_prior = out["M2"].rolling(window=L, min_periods=L).median().shift(1)
    labels = np.full(len(out), None, dtype=object)
    m2 = out["M2"].to_numpy(dtype=float)
    med = med_prior.to_numpy(dtype=float)
    valid = np.isfinite(m2) & np.isfinite(med)
    labels[valid & (m2 > med)] = HIGH
    labels[valid & (m2 <= med)] = LOW
    out["label"] = labels

    # F_t = mean(|ln ret| for j=1..H); require H finite future returns
    # At t: mean of abs_log_ret[t+1 : t+H+1]
    s = abs_log_ret.shift(-1)
    fwd = s.iloc[::-1].rolling(window=H, min_periods=H).mean().iloc[::-1]
    out["F"] = fwd.to_numpy(dtype=float)
    return out


def _smd(labels: np.ndarray, values: np.ndarray, high: str = HIGH, low: str = LOW) -> float | None:
    h = values[labels == high]
    lo = values[labels == low]
    h = h[np.isfinite(h)]
    lo = lo[np.isfinite(lo)]
    n_h, n_l = h.size, lo.size
    if n_h < 2 or n_l < 2:
        return None
    mu_h, mu_l = h.mean(), lo.mean()
    s_h2, s_l2 = h.var(ddof=1), lo.var(ddof=1)
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
    base = np.array([HIGH] * n_high + [LOW] * (n - n_high), dtype=object)
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


def _run_lengths(labels_full: np.ndarray) -> np.ndarray:
    """NO-label bars break runs (Fill §4.2)."""
    lengths: list[int] = []
    cur = None
    n = 0
    for lab in labels_full:
        if lab not in (HIGH, LOW):
            if n > 0:
                lengths.append(n)
            cur = None
            n = 0
            continue
        if lab == cur:
            n += 1
        else:
            if n > 0:
                lengths.append(n)
            cur = lab
            n = 1
    if n > 0:
        lengths.append(n)
    return np.asarray(lengths, dtype=float)


def _null_q95_mean_run_length(
    labels_full: np.ndarray,
    rng: np.random.Generator,
) -> float | None:
    """N1: iid shuffle HIGH/LOW among labeled positions; NO-label fixed."""
    idx = np.array([i for i, lab in enumerate(labels_full) if lab in (HIGH, LOW)], dtype=int)
    if idx.size == 0:
        return None
    labs = labels_full[idx]
    n_high = int((labs == HIGH).sum())
    base = np.array([HIGH] * n_high + [LOW] * (idx.size - n_high), dtype=object)
    null_means = np.empty(N_PERM, dtype=float)
    for i in range(N_PERM):
        perm = base.copy()
        rng.shuffle(perm)
        arr = labels_full.copy()
        arr[idx] = perm
        runs = _run_lengths(arr)
        null_means[i] = float(runs.mean()) if runs.size else np.nan
    null_means = null_means[np.isfinite(null_means)]
    if null_means.size == 0:
        return None
    return float(np.quantile(null_means, 0.95))


def _eval_e1(symbol: str, feat: pd.DataFrame) -> E1Result:
    full = feat[(feat["dt_cst"] >= FULL_START) & (feat["dt_cst"] <= FULL_END)]
    mask = full["label"].isin([HIGH, LOW]) & np.isfinite(full["F"].to_numpy(dtype=float))
    sample = full.loc[mask]
    labels = sample["label"].to_numpy()
    fvals = sample["F"].to_numpy(dtype=float)
    m2 = sample["M2"].to_numpy(dtype=float)
    n_h = int((labels == HIGH).sum())
    n_l = int((labels == LOW).sum())
    if n_h < MIN_SAMPLE_PER_LABEL or n_l < MIN_SAMPLE_PER_LABEL:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_fwd=None,
            n1_q95=None,
            smd_m2_diagnostic=None,
            pass_e1=None,
            status="INFEASIBLE",
            detail=f"min_sample_per_label={MIN_SAMPLE_PER_LABEL} not met",
        )
    smd_fwd = _smd(labels, fvals)
    smd_m2 = _smd(labels, m2)  # N2 diagnostic only
    if smd_fwd is None:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_fwd=None,
            n1_q95=None,
            smd_m2_diagnostic=smd_m2,
            pass_e1=None,
            status="INFEASIBLE",
            detail="SMD_FWD_ABSRET INFEASIBLE",
        )
    rng = np.random.default_rng(RNG_SEED + SYM_RNG_OFFSET[symbol])
    q95 = _null_q95_smd(labels, fvals, n_h, rng)
    if q95 is None:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_fwd=smd_fwd,
            n1_q95=None,
            smd_m2_diagnostic=smd_m2,
            pass_e1=None,
            status="INFEASIBLE",
            detail="N1 null infeasible",
        )
    passed = bool(smd_fwd > q95)
    return E1Result(
        symbol=symbol,
        n_high=n_h,
        n_low=n_l,
        smd_fwd=smd_fwd,
        n1_q95=q95,
        smd_m2_diagnostic=smd_m2,
        pass_e1=passed,
        status="PASS" if passed else "FAIL",
    )


def _eval_e2(feat: pd.DataFrame, *, e1_retain: bool) -> dict:
    if not e1_retain:
        return {"status": "skipped", "band": "skipped", "reason": "L1-E1 not Retain"}
    full = feat[(feat["dt_cst"] >= FULL_START) & (feat["dt_cst"] <= FULL_END)]
    labels_full = full["label"].to_numpy()
    runs = _run_lengths(labels_full)
    if runs.size < MIN_RUNS:
        return {
            "status": "INFEASIBLE",
            "band": "Infeasible",
            "detail": f"min_runs={MIN_RUNS} not met",
            "n_runs": int(runs.size),
        }
    obs = float(runs.mean())
    rng = np.random.default_rng(RNG_SEED + 100)
    q95 = _null_q95_mean_run_length(labels_full, rng)
    if q95 is None:
        return {
            "status": "INFEASIBLE",
            "band": "Infeasible",
            "mean_run_length": obs,
            "n_runs": int(runs.size),
        }
    passed = bool(obs > q95)
    return {
        "status": "PASS" if passed else "FAIL",
        "band": "Retain" if passed else "Reject",
        "mean_run_length": obs,
        "n_runs": int(runs.size),
        "n1_q95": q95,
        "pass_e2": passed,
        "null_role": "N1_primary",
    }


def _aggregate(e1: dict[str, E1Result], e2: dict) -> dict:
    """Fill §4.4 aggregate — sealed before results; no post-hoc edit."""
    primary = e1[PRIMARY]
    transfer_pass = {sym: (e1[sym].pass_e1 is True) for sym in TRANSFER}
    e3_all_pass = all(transfer_pass.values())
    e3_any_fail = any(e1[sym].pass_e1 is False for sym in TRANSFER)
    e3_any_inf = any(e1[sym].pass_e1 is None for sym in TRANSFER)

    if primary.status == "INFEASIBLE":
        e1_band = "Infeasible"
    elif primary.pass_e1 is True:
        e1_band = "Retain"
    else:
        e1_band = "Reject"

    e2_band = e2.get("band", "skipped")
    if e3_all_pass:
        e3_band = "Retain"
    elif e3_any_fail:
        e3_band = "Reject"
    elif e3_any_inf:
        e3_band = "Infeasible"
    else:
        e3_band = "Narrow"

    # PASS: E1 Retain, E2 not Reject, E3 Retain, N1 as expected (embedded in E1/E2)
    if e1_band == "Infeasible" or e3_band == "Infeasible" or e2_band == "Infeasible":
        outcome = "INFEASIBLE"
    elif e1_band == "Reject" or e3_band == "Reject" or e2_band == "Reject":
        outcome = "FAIL"
    elif e1_band == "Retain" and e3_band == "Retain" and e2_band == "Retain":
        outcome = "PASS"
    elif e1_band == "Retain":
        outcome = "PARTIAL"
    else:
        outcome = "FAIL"

    knowledge_action_preview = {
        "PASS": "STRENGTHEN (Independence / P4-facing) — requires Knowledge Review",
        "PARTIAL": "NARROW — requires Knowledge Review",
        "FAIL": "NARROW / DOWNGRADE — requires Knowledge Review; FAIL ≠ K001 false",
        "INFEASIBLE": "No Knowledge Action",
        "INVALID": "No Knowledge Action",
    }.get(outcome, "No Knowledge Action")

    return {
        "L1_E1_band": e1_band,
        "L1_E2_band": e2_band,
        "L1_E3_band": e3_band,
        "transfer_pass": transfer_pass,
        "outcome": outcome,
        "knowledge_action_preview": knowledge_action_preview,
        "knowledge_update_authorized": False,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not MANIFEST_PATH.is_file():
        print("[error] Manifest missing — abort", flush=True)
        return 2

    revision = _git_revision()
    print(f"[L1] verify LER seal ...", flush=True)
    ler_hash = _verify_ler_seal()
    print(f"[L1] LER hash OK {ler_hash[:16]}...", flush=True)
    _update_manifest_start(revision, ler_hash)
    started = datetime.now(timezone.utc).isoformat()
    print(f"[CAP_CTX_001_L1_RUN001] start revision={revision}", flush=True)

    coverage = []
    features: dict[str, pd.DataFrame] = {}
    for sym in UNIVERSE:
        df = _load_symbol(sym)
        cov = _check_coverage(df, sym)
        coverage.append(cov)
        print(f"[coverage] {cov}", flush=True)
        if not cov["ok"]:
            payload = {
                "run_id": RUN_ID,
                "decision": "INFEASIBLE",
                "reason": "coverage_gap",
                "coverage": coverage,
                "registered_knowledge_action": "NO_UPGRADE",
            }
            (OUT_DIR / "evaluation.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            _finalize_manifest("INFEASIBLE_COVERAGE", {"coverage": coverage})
            return 2
        print(f"[GEN-L1] features {sym} ...", flush=True)
        features[sym] = _compute_gen_features(df)

    e1_results: dict[str, E1Result] = {}
    for sym in UNIVERSE:
        print(f"[L1-E1] {sym} ...", flush=True)
        e1_results[sym] = _eval_e1(sym, features[sym])
        print(f"[L1-E1] {e1_results[sym]}", flush=True)

    e1_retain = e1_results[PRIMARY].pass_e1 is True
    print("[L1-E2] rb ...", flush=True)
    e2 = _eval_e2(features[PRIMARY], e1_retain=e1_retain)
    print(f"[L1-E2] {e2}", flush=True)

    agg = _aggregate(e1_results, e2)
    outcome = agg["outcome"]
    print(f"[aggregate] outcome={outcome}", flush=True)

    evaluation = {
        "schema": "CAP_CTX_001_L1_Evaluation_v1",
        "run_id": RUN_ID,
        "eq": "EQ-CTX-L1",
        "gen_recipe": "GEN-L1-v0.2",
        "ler_version": "LER-CTX-L1 v0.2",
        "ler_content_sha256": ler_hash,
        "primary_null": "N1",
        "diagnostic_null": "N2",
        "coverage": coverage,
        "L1_E1": {sym: asdict(e1_results[sym]) for sym in UNIVERSE},
        "L1_E2": e2,
        "L1_E3": {
            "transfer": list(TRANSFER),
            "aggregation": "3/3",
            "results": {sym: asdict(e1_results[sym]) for sym in TRANSFER},
            "band": agg["L1_E3_band"],
            "transfer_pass": agg["transfer_pass"],
        },
        "aggregate": agg,
        "decision": outcome,
        "n2_diagnostic_note": (
            "smd_m2_diagnostic is N2 only; must not upgrade Outcome to PASS"
        ),
        "dependency_disclosure": {
            "dependency_removed": ["label_generation_dependency"],
            "dependency_retained": [
                "dataset",
                "universe",
                "market_structure",
                "timeframe",
            ],
        },
        "non_claims": [
            "not_knowledge_decision",
            "not_gate_pass",
            "not_capability_candidate",
            "not_strategy",
            "not_alpha",
            "not_fully_independent",
            "FAIL_neq_K001_false",
        ],
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_revision": revision,
    }
    (OUT_DIR / "evaluation.json").write_text(
        json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    evidence = {
        "schema": "CAP_CTX_001_L1_EvidenceRecord_v1",
        "run_id": RUN_ID,
        "campaign_id": "CAP-CTX-001",
        "evidence_type": "independence_repair_l1",
        "parent_knowledge": "K001",
        "outcome": outcome,
        "evaluation_path": str((OUT_DIR / "evaluation.json").relative_to(ROOT).as_posix()),
        "manifest_path": str(MANIFEST_PATH.relative_to(ROOT).as_posix()),
        "ler_path": str(LER_PATH.relative_to(ROOT).as_posix()),
        "dependency_disclosure": evaluation["dependency_disclosure"],
        "knowledge_update_authorized": False,
        "gate_review_authorized": False,
        "observation_authorization": AUTH_COMMAND,
        "integrity": {
            "anti_optimization": True,
            "n1_primary": True,
            "n2_diagnostic_only": True,
            "ler_sealed_before_eval": True,
        },
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "evidence_record.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    _finalize_manifest(
        "OBSERVATION_COMPLETE",
        {
            "outcome": outcome,
            "evaluation": "evaluation.json",
            "evidence_record": "evidence_record.json",
        },
    )
    print(f"[done] outcome={outcome} → {OUT_DIR}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
