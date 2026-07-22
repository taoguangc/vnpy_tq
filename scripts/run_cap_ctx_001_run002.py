"""CAP_CTX_001_RUN002 — Temporal OOS Cross Evidence Observation + Evaluation.

Protocol inherited from CAP_CTX_001_RUN001 unless overridden by registered
temporal scope. Produces evaluation artifacts only.
Does NOT claim Knowledge Decision / Gate / Alpha.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
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
RUN_ID = "CAP_CTX_001_RUN002"
PARENT_RUN_ID = "CAP_CTX_001_RUN001"
OUT_DIR = ROOT / "research" / "output" / "evidence" / RUN_ID
MANIFEST_PATH = OUT_DIR / "CAP_CTX_001_RUN_MANIFEST.json"

UNIVERSE = ("rb", "i", "MA")
PRIMARY = "rb"
TRANSFER = ("i", "MA")

FULL_START = pd.Timestamp("2022-01-01", tz=CST)
FULL_END = pd.Timestamp("2023-12-31 23:59:59", tz=CST)
# Causal warmup before Full (W=20, L=240); excluded from evaluation stats
WARMUP_START = pd.Timestamp("2021-10-01", tz=CST)
COVERAGE_MONTHS_START = "2022-01"
COVERAGE_MONTHS_END = "2023-12"

W = 20
L = 240
N_PERM = 200
RNG_SEED = 20240721
BLOCK_SIZE = 60
MIN_SAMPLE_PER_LABEL = 5000
MIN_RUNS = 100


@dataclass(frozen=True)
class E1Result:
    symbol: str
    n_high: int
    n_low: int
    smd_m1: float | None
    smd_m2: float | None
    n1_q95: float | None
    pass_e1: bool | None
    status: str
    detail: str = ""


def _git_revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _update_manifest_start(revision: str) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    manifest["observation_start_authorized"] = True
    manifest["observation_status"] = "RUNNING"
    manifest["execution_state"] = "OBSERVATION_AUTHORIZED_AND_STARTED"
    manifest["observation_execution"] = {
        "authorized_command": "Authorize Observation Execution for CAP_CTX_001_RUN002",
        "started_at_utc": now,
        "code_revision_at_start": revision,
        "parent": PARENT_RUN_ID,
        "eq": "EQ-CTX-002",
    }
    manifest["environment_identity"]["code_revision_at_observation_start"] = revision
    manifest["note"] = (
        "RUN002 Cross Evidence Observation started under Appendix A. "
        "Protocol inherited from RUN001; temporal scope override only. "
        "No Knowledge Decision / Gate / Alpha claim from this Manifest."
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
    """Full-window coverage: require bars in every calendar month; disclose max gap.

    Long calendar gaps (weekends / CNY) are expected on futures 1m streams and
    must NOT trigger STOP. STOP only if a month inside the frozen window has
    zero bars (missing contract coverage) or the window is empty.
    """
    full = df[(df["dt_cst"] >= FULL_START) & (df["dt_cst"] <= FULL_END)]
    if full.empty:
        return {
            "symbol": symbol,
            "ok": False,
            "reason": "empty_full_window",
            "max_gap_hours": None,
            "missing_months": [],
        }
    months = pd.period_range(COVERAGE_MONTHS_START, COVERAGE_MONTHS_END, freq="M")
    present = set(full["dt_cst"].dt.to_period("M").unique())
    missing_months = [str(m) for m in months if m not in present]
    deltas = full["dt_cst"].diff().dropna()
    max_gap = deltas.max()
    ok = len(missing_months) == 0
    return {
        "symbol": symbol,
        "ok": ok,
        "reason": None if ok else "missing_calendar_months",
        "missing_months": missing_months,
        "n_bars_full": int(len(full)),
        "max_gap_hours": float(max_gap / pd.Timedelta(hours=1)) if pd.notna(max_gap) else None,
        "full_start": str(full["dt_cst"].iloc[0]),
        "full_end": str(full["dt_cst"].iloc[-1]),
        "gap_policy": (
            f"STOP iff any calendar month in {COVERAGE_MONTHS_START}.."
            f"{COVERAGE_MONTHS_END} has zero bars; "
            "weekend/holiday gaps disclosed via max_gap_hours only"
        ),
    }


def _compute_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["close"].astype(float)
    log_ret = np.log(close / close.shift(1))
    # sample stdev ddof=1 over W returns ending at t
    out["M1"] = log_ret.rolling(window=W, min_periods=W).std(ddof=1)
    abs_move = (close - close.shift(W)).abs()
    path = close.diff().abs().rolling(window=W, min_periods=W).sum()
    out["M2"] = abs_move / path.replace(0.0, np.nan)

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


def _smd(values: np.ndarray, labels: np.ndarray, target_values: np.ndarray | None = None) -> float | None:
    """SMD on target_values (default values) split by labels HIGH/LOW."""
    x = values if target_values is None else target_values
    high = x[labels == "HIGH_VOL"]
    low = x[labels == "LOW_VOL"]
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
    n_h = int((labels == "HIGH_VOL").sum())
    n_l = int((labels == "LOW_VOL").sum())
    if n_h < MIN_SAMPLE_PER_LABEL or n_l < MIN_SAMPLE_PER_LABEL:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=None,
            smd_m2=None,
            n1_q95=None,
            pass_e1=None,
            status="HOLD",
            detail=f"min_sample_per_label={MIN_SAMPLE_PER_LABEL} not met",
        )
    smd_m1 = _smd(m1, labels, m1)
    smd_m2 = _smd(m1, labels, m2)
    if smd_m1 is None:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=None,
            smd_m2=smd_m2,
            n1_q95=None,
            pass_e1=None,
            status="HOLD",
            detail="SMD_M1 INFEASIBLE",
        )

    # N1 iid label permutation preserving counts
    n = labels.size
    n_high = n_h
    null_smds = np.empty(N_PERM, dtype=float)
    base = np.array(
        ["HIGH_VOL"] * n_high + ["LOW_VOL"] * (n - n_high),
        dtype=object,
    )
    for i in range(N_PERM):
        perm = base.copy()
        rng.shuffle(perm)
        val = _smd(m1, perm, m1)
        null_smds[i] = np.nan if val is None else val
    null_smds = null_smds[np.isfinite(null_smds)]
    if null_smds.size == 0:
        return E1Result(
            symbol=symbol,
            n_high=n_h,
            n_low=n_l,
            smd_m1=smd_m1,
            smd_m2=smd_m2,
            n1_q95=None,
            pass_e1=None,
            status="HOLD",
            detail="N1 null infeasible",
        )
    q95 = float(np.quantile(null_smds, 0.95))
    passed = bool(smd_m1 > q95)
    return E1Result(
        symbol=symbol,
        n_high=n_h,
        n_low=n_l,
        smd_m1=smd_m1,
        smd_m2=smd_m2,
        n1_q95=q95,
        pass_e1=passed,
        status="PASS" if passed else "FAIL",
    )


def _eval_e2(feat: pd.DataFrame, rng: np.random.Generator, *, e1_pass: bool) -> dict:
    if not e1_pass:
        return {"status": "skipped", "reason": "E1 not PASS"}
    full = feat[(feat["dt_cst"] >= FULL_START) & (feat["dt_cst"] <= FULL_END)]
    mask = full["label"].isin(["HIGH_VOL", "LOW_VOL"])
    labels = full.loc[mask, "label"].to_numpy()
    runs = _run_lengths(labels)
    if runs.size < MIN_RUNS:
        return {
            "status": "HOLD",
            "detail": f"min_runs={MIN_RUNS} not met",
            "n_runs": int(runs.size),
            "mean_run_length": float(runs.mean()) if runs.size else None,
        }
    obs = float(runs.mean())
    null_means = np.empty(N_PERM, dtype=float)
    n = labels.size
    for i in range(N_PERM):
        # block label permutation
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
    _update_manifest_start(revision)
    started = datetime.now(timezone.utc).isoformat()
    print(f"[CAP_CTX_001_RUN002] start revision={revision}", flush=True)

    coverage = []
    features: dict[str, pd.DataFrame] = {}
    for sym in UNIVERSE:
        df = _load_symbol(sym)
        cov = _check_coverage_gap(df, sym)
        coverage.append(cov)
        print(f"[coverage] {cov}", flush=True)
        if not cov["ok"]:
            payload = {
                "decision": "HOLD",
                "reason": "coverage_gap_STOP",
                "coverage": coverage,
                "claim_boundary": "No Capability claim. Incomplete coverage.",
            }
            (OUT_DIR / "evaluation.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            _finalize_manifest("STOPPED_COVERAGE", {"coverage": coverage})
            print("[STOP] coverage rule triggered", flush=True)
            return 2
        print(f"[features] {sym} ...", flush=True)
        features[sym] = _compute_features(df)

    e1_results = {}
    for sym in UNIVERSE:
        print(f"[E1] {sym} ...", flush=True)
        sym_rng = np.random.default_rng(
            RNG_SEED + (0 if sym == "rb" else 1 if sym == "i" else 2)
        )
        e1_results[sym] = _eval_e1(sym, features[sym], sym_rng)
        print(f"[E1] {e1_results[sym]}", flush=True)

    primary_e1 = e1_results[PRIMARY]
    e1_pass_primary = primary_e1.pass_e1 is True

    print("[E2] rb ...", flush=True)
    e2 = _eval_e2(
        features[PRIMARY],
        np.random.default_rng(RNG_SEED + 100),
        e1_pass=e1_pass_primary,
    )
    print(f"[E2] {e2}", flush=True)

    print("[E3] transfer ...", flush=True)
    transfer_pass = {
        sym: (e1_results[sym].pass_e1 is True) for sym in TRANSFER
    }
    e3_general = all(transfer_pass.values())
    e3 = {
        "transfer_e1_pass": transfer_pass,
        "general_capability_supported": e3_general,
        "n3_isolated": bool(e1_pass_primary and not e3_general),
        "rule": "E1 Pass on i AND MA required for general claim",
    }
    print(f"[E3] {e3}", flush=True)

    # Cross Evidence: Registered Knowledge Actions only (not Knowledge Decision).
    # Protocol decision path inherited from RUN001; mapped to C-K001 actions.
    if primary_e1.status == "HOLD" or e2.get("status") == "HOLD":
        decision = "INFEASIBLE"
        registered_knowledge_action = "NO_UPGRADE"
        cross_evidence_result = "INFEASIBLE"
    elif e1_pass_primary and e2.get("pass_e2") and e3_general:
        decision = "SUPPORTED"
        registered_knowledge_action = "STRENGTHEN"
        cross_evidence_result = "SUPPORTED"
    elif e1_pass_primary and e3.get("n3_isolated"):
        decision = "PARTIAL"
        registered_knowledge_action = "NARROW"
        cross_evidence_result = "PARTIAL"
    elif not e1_pass_primary:
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
            "n1_q95": r.n1_q95,
            "pass_e1": r.pass_e1,
            "status": r.status,
            "detail": r.detail,
        }

    evaluation = {
        "run_id": RUN_ID,
        "parent": PARENT_RUN_ID,
        "experiment_id": RUN_ID,
        "campaign_id": "CAP-CTX-001",
        "eq": "EQ-CTX-002",
        "role": "cross_evidence_temporal_oos",
        "protocol_inheritance": (
            "Protocol inherited from CAP_CTX_001_RUN001 unless explicitly "
            "overridden by registered temporal scope."
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
            "full_start": str(FULL_START),
            "full_end": str(FULL_END),
            "warmup_start": str(WARMUP_START),
            "warmup_excluded_from_stats": True,
        },
        "coverage": coverage,
        "E1": {sym: e1_dict(e1_results[sym]) for sym in UNIVERSE},
        "E2": e2,
        "E3": e3,
        "decision": decision,
        "cross_evidence_result": cross_evidence_result,
        "registered_knowledge_action": registered_knowledge_action,
        "methodological_note": (
            "E1 SMD_M1 is partly definition-coupled (labels from M1); "
            "E1 = supporting only. Interpret with E2, E3, and SMD_M2."
        ),
        "claim_boundary": {
            "allowed": (
                "Under RUN002 OOS conditions, evidence consistent / "
                "inconsistent with RUN001 descriptive structure; "
                "Registered Knowledge Action only."
            ),
            "forbidden": [
                "unconditional K001 upgrade",
                "Knowledge Decision without Review",
                "market state discovered",
                "tradable alpha found",
                "Context Capability Gate auto PASS",
                "RC001 Accepted",
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
        "campaign": "CAP-CTX-001",
        "eq": "EQ-CTX-002",
        "role": "cross_evidence_temporal_oos",
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
        "note": (
            "Registered Knowledge Action is pre-mapped only; "
            "final K001 Knowledge Decision requires separate Review."
        ),
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
        f"[done] decision={decision} "
        f"cross_evidence_result={cross_evidence_result} "
        f"registered_knowledge_action={registered_knowledge_action}",
        flush=True,
    )
    print(f"[done] wrote {eval_path}", flush=True)
    print(f"[done] wrote {ev_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
