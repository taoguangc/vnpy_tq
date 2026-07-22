"""RC001_A_EXP001 — Controlled Context Filter experiment (frozen Spec).

Authorize RC001-A Execution only. Does not modify OPP16 / FP / EF.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from context_engine.publisher import ContextStatePublisher, PublisherConfig  # noqa: E402
from scripts.tq_rollover_data import build_stitched_raw_frame  # noqa: E402
from strategies.paaf.detectors.opp16_two_bar_reversal import (  # noqa: E402
    DEFAULT_BODY_RATIO,
    OPP16TwoBarReversalDetector,
)
from strategies.paaf.domain import Context, Direction, MarketState, Session  # noqa: E402
from tools.tq_paths import symbol_dir  # noqa: E402

CST = ZoneInfo("Asia/Shanghai")
WARMUP_START = pd.Timestamp("2023-10-01", tz=CST)
EVAL_START = pd.Timestamp("2024-01-01", tz=CST)
EVAL_END = pd.Timestamp("2025-12-31 23:59:59", tz=CST)

OPP16_PATH = ROOT / "strategies" / "paaf" / "detectors" / "opp16_two_bar_reversal.py"
OPP16_SHA256_LOCKED = (
    "ddb8378defa95ed1e2f3ccdd3cfd2ee3fbc25816a576524c21b6a42284ae9954"
)
RB_FP_LOCKED = {
    "manifest.json": "bc62c8b606bf5c5018448e54aad841aa14a58f60482042f561e80f99ba8ed0fa",
    "dominant_windows.json": "051e5b48154a2228ec4e06ed361d8ebed40ba20f2fccec8fc8c953f9a169929b",
    "rollover_map.parquet": "170102046bdbe339aad14de20a9f95463838da18b077fab10e54381102e92a8e",
}

SIZE = 10
RATE = 1e-4
SLIPPAGE = 1.0  # price units
CAPITAL = 200_000.0
TIME_STOP_5M = 60
FILTER_POLICY = "FP-RC001-A-v1"
EXIT_FAMILY = "EF-RC001-A-v1"

OUT_DIR = ROOT / "research" / "output" / "evidence" / "RC001_A_EXP001"


Permission = Literal["ALLOW", "BLOCK", "MONITOR_ONLY"]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _integrity() -> dict[str, Any]:
    opp_hash = _sha256_file(OPP16_PATH)
    data_dir = symbol_dir("rb")
    fps = {name: _sha256_file(data_dir / name) for name in RB_FP_LOCKED}
    mismatches = {
        k: {"expected": RB_FP_LOCKED[k], "observed": fps[k]}
        for k in RB_FP_LOCKED
        if fps.get(k) != RB_FP_LOCKED[k]
    }
    ok = opp_hash == OPP16_SHA256_LOCKED and not mismatches
    return {
        "pass": ok,
        "opp16_sha256": opp_hash,
        "opp16_sha256_match": opp_hash == OPP16_SHA256_LOCKED,
        "dataset_fingerprints": fps,
        "fingerprint_mismatches": mismatches,
        "code_revision": _git_head(),
        "body_ratio": DEFAULT_BODY_RATIO,
        "filter_policy": FILTER_POLICY,
        "exit_family": EXIT_FAMILY,
        "size": SIZE,
        "rate": RATE,
        "slippage": SLIPPAGE,
    }


def _build_5m(frame_1m: pd.DataFrame) -> pd.DataFrame:
    work = frame_1m.set_index("dt_cst").sort_index()
    agg = (
        work.resample("5min", label="left", closed="left")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
            }
        )
        .dropna(subset=["open", "high", "low", "close"])
    )
    return agg.reset_index()


def _ohlc_window(frame: pd.DataFrame, end_index: int) -> SimpleNamespace:
    start = max(0, end_index - 1)
    sl = frame.iloc[start : end_index + 1]
    return SimpleNamespace(
        open=tuple(float(x) for x in sl["open"]),
        high=tuple(float(x) for x in sl["high"]),
        low=tuple(float(x) for x in sl["low"]),
        close=tuple(float(x) for x in sl["close"]),
        count=len(sl),
        inited=len(sl) >= 2,
    )


def _fp_permission(validity: str, context_state: str) -> Permission:
    if validity == "INVALID" or context_state == "invalid":
        return "BLOCK"
    if validity == "DEGRADED":
        return "BLOCK"
    if context_state == "compression" and validity == "VALID":
        return "ALLOW"
    if context_state == "expansion" and validity == "VALID":
        return "MONITOR_ONLY"
    return "BLOCK"


@dataclass
class Signal:
    idx_5m: int
    dt: pd.Timestamp
    direction: str
    entry: float
    stop: float
    permission: Permission
    context_state: str
    validity: str


@dataclass
class Trade:
    arm: str
    signal_dt: str
    direction: str
    entry: float
    stop: float
    exit: float
    exit_reason: str
    exit_dt: str
    pnl: float
    r_multiple: float
    bars_5m_held: int
    permission: Permission | None = None
    context_state: str | None = None


def _commission(price: float, volume: float = 1.0) -> float:
    return abs(price) * SIZE * volume * RATE


def _slip_cost(volume: float = 1.0) -> float:
    return SLIPPAGE * SIZE * volume


def _simulate_trade(
    *,
    arm: str,
    sig: Signal,
    frame_1m: pd.DataFrame,
    idx_1m_by_dt: dict[Any, int],
    frame_5m: pd.DataFrame,
) -> Trade | None:
    """EF-RC001-A-v1 on 1m after 5m signal."""
    entry_px = float(sig.entry)
    stop_px = float(sig.stop)
    risk = abs(entry_px - stop_px)
    if risk <= 0 or not np.isfinite(risk):
        return None

    # entry fill with slippage
    if sig.direction == "LONG":
        fill = entry_px + SLIPPAGE
    else:
        fill = entry_px - SLIPPAGE

    # find 1m index at/after signal bar end (5m left label → +5min)
    bar_end = sig.dt + pd.Timedelta(minutes=5)
    # start monitoring from first 1m >= bar_end - 1min (include close bar) 
    # Spec: entry at signal close; stop on subsequent 1m
    start_1m = idx_1m_by_dt.get(pd.Timestamp(sig.dt))
    # use bars after the 5m window's last minute
    candidates = frame_1m.index[frame_1m["dt_cst"] >= bar_end - pd.Timedelta(minutes=1)]
    if len(candidates) == 0:
        return None
    i0 = int(candidates[0])

    entry_comm = _commission(fill)
    entry_slip = _slip_cost()
    held_5m = 0
    last_5m_boundary = sig.dt

    for i in range(i0, len(frame_1m)):
        row = frame_1m.iloc[i]
        ts = pd.Timestamp(row["dt_cst"])
        hi = float(row["high"])
        lo = float(row["low"])
        cl = float(row["close"])

        # stop priority
        if sig.direction == "LONG" and lo <= stop_px:
            exit_px = stop_px - SLIPPAGE
            pnl = (exit_px - fill) * SIZE - entry_comm - _commission(exit_px) - entry_slip - _slip_cost()
            return Trade(
                arm=arm,
                signal_dt=str(sig.dt),
                direction=sig.direction,
                entry=fill,
                stop=stop_px,
                exit=exit_px,
                exit_reason="stop",
                exit_dt=str(ts),
                pnl=float(pnl),
                r_multiple=float(pnl / (risk * SIZE)),
                bars_5m_held=held_5m,
                permission=sig.permission,
                context_state=sig.context_state,
            )
        if sig.direction == "SHORT" and hi >= stop_px:
            exit_px = stop_px + SLIPPAGE
            pnl = (fill - exit_px) * SIZE - entry_comm - _commission(exit_px) - entry_slip - _slip_cost()
            return Trade(
                arm=arm,
                signal_dt=str(sig.dt),
                direction=sig.direction,
                entry=fill,
                stop=stop_px,
                exit=exit_px,
                exit_reason="stop",
                exit_dt=str(ts),
                pnl=float(pnl),
                r_multiple=float(pnl / (risk * SIZE)),
                bars_5m_held=held_5m,
                permission=sig.permission,
                context_state=sig.context_state,
            )

        # count completed 5m boundaries after entry
        # 5m left-labeled starts: advance when ts crosses next 5m close
        elapsed = (ts - sig.dt) / pd.Timedelta(minutes=5)
        held_5m = int(elapsed)
        if held_5m >= TIME_STOP_5M:
            if sig.direction == "LONG":
                exit_px = cl - SLIPPAGE
                pnl = (exit_px - fill) * SIZE - entry_comm - _commission(exit_px) - entry_slip - _slip_cost()
            else:
                exit_px = cl + SLIPPAGE
                pnl = (fill - exit_px) * SIZE - entry_comm - _commission(exit_px) - entry_slip - _slip_cost()
            return Trade(
                arm=arm,
                signal_dt=str(sig.dt),
                direction=sig.direction,
                entry=fill,
                stop=stop_px,
                exit=float(exit_px),
                exit_reason="time_stop",
                exit_dt=str(ts),
                pnl=float(pnl),
                r_multiple=float(pnl / (risk * SIZE)),
                bars_5m_held=held_5m,
                permission=sig.permission,
                context_state=sig.context_state,
            )

    # EOD flatten
    row = frame_1m.iloc[-1]
    cl = float(row["close"])
    ts = pd.Timestamp(row["dt_cst"])
    if sig.direction == "LONG":
        exit_px = cl - SLIPPAGE
        pnl = (exit_px - fill) * SIZE - entry_comm - _commission(exit_px) - entry_slip - _slip_cost()
    else:
        exit_px = cl + SLIPPAGE
        pnl = (fill - exit_px) * SIZE - entry_comm - _commission(exit_px) - entry_slip - _slip_cost()
    return Trade(
        arm=arm,
        signal_dt=str(sig.dt),
        direction=sig.direction,
        entry=fill,
        stop=stop_px,
        exit=float(exit_px),
        exit_reason="eod_flat",
        exit_dt=str(ts),
        pnl=float(pnl),
        r_multiple=float(pnl / (risk * SIZE)),
        bars_5m_held=held_5m,
        permission=sig.permission,
        context_state=sig.context_state,
    )


def _max_dd(pnls: list[float]) -> float:
    equity = CAPITAL
    peak = equity
    max_dd = 0.0
    for p in pnls:
        equity += p
        peak = max(peak, equity)
        max_dd = min(max_dd, equity - peak)
    return float(max_dd)


def _sharpe(pnls: list[float]) -> float:
    if len(pnls) < 2:
        return float("nan")
    arr = np.asarray(pnls, dtype=float)
    sd = float(arr.std(ddof=1))
    if sd == 0:
        return float("nan")
    # trade-level pseudo Sharpe (not annualized) — auxiliary only
    return float(arr.mean() / sd * np.sqrt(len(arr)))


def _pf(pnls: list[float]) -> float:
    gains = sum(p for p in pnls if p > 0)
    losses = -sum(p for p in pnls if p < 0)
    if losses <= 0:
        return float("inf") if gains > 0 else float("nan")
    return float(gains / losses)


def run() -> int:
    print("[RC001-A] integrity ...", flush=True)
    integrity = _integrity()
    if not integrity["pass"]:
        print("[RC001-A] INTEGRITY FAIL", json.dumps(integrity, indent=2), flush=True)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "integrity_fail.json").write_text(
            json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
        )
        return 2

    print("[RC001-A] load rb ...", flush=True)
    frame_1m = build_stitched_raw_frame("rb")
    frame_1m = frame_1m.copy()
    frame_1m["dt_cst"] = pd.to_datetime(frame_1m["dt_cst"], utc=False)
    if frame_1m["dt_cst"].dt.tz is None:
        frame_1m["dt_cst"] = frame_1m["dt_cst"].dt.tz_localize(CST)
    else:
        frame_1m["dt_cst"] = frame_1m["dt_cst"].dt.tz_convert(CST)
    frame_1m = frame_1m.sort_values("dt_cst").drop_duplicates("dt_cst", keep="last")
    frame_1m = frame_1m[
        (frame_1m["dt_cst"] >= WARMUP_START) & (frame_1m["dt_cst"] <= EVAL_END)
    ].reset_index(drop=True)

    print("[RC001-A] context publish 1m ...", flush=True)
    pub = ContextStatePublisher(PublisherConfig(instrument="rb", manifest_id="RC001_A"))
    ctx_by_1m: dict[pd.Timestamp, Any] = {}
    for row in frame_1m.itertuples(index=False):
        st = pub.update_bar(
            timestamp=pd.Timestamp(row.dt_cst),
            high=float(row.high),
            low=float(row.low),
        )
        ctx_by_1m[pd.Timestamp(row.dt_cst)] = st

    print("[RC001-A] build 5m + OPP16 signals ...", flush=True)
    frame_5m = _build_5m(frame_1m)
    detector = OPP16TwoBarReversalDetector(body_ratio=DEFAULT_BODY_RATIO)
    dummy_ctx = Context(
        symbol="rb",
        market_state=MarketState.UNKNOWN,
        session=Session.UNKNOWN,
    )

    signals: list[Signal] = []
    for i in range(len(frame_5m)):
        dt = pd.Timestamp(frame_5m["dt_cst"].iloc[i])
        if dt < EVAL_START or dt > EVAL_END:
            continue
        result = detector.detect(_ohlc_window(frame_5m, i), dummy_ctx)
        if result is None or result.direction in (Direction.NONE, None):
            continue
        # Context at last 1m inside 5m window [dt, dt+5m)
        window_end = dt + pd.Timedelta(minutes=5)
        ones = [
            t
            for t in ctx_by_1m
            if dt <= t < window_end
        ]
        if not ones:
            # fallback nearest <= window_end-1m
            prior = [t for t in ctx_by_1m if t < window_end]
            if not prior:
                continue
            st = ctx_by_1m[max(prior)]
        else:
            st = ctx_by_1m[max(ones)]
        cs = st.descriptive_state.get("context_state", "invalid")
        perm = _fp_permission(st.validity, cs)
        signals.append(
            Signal(
                idx_5m=i,
                dt=dt,
                direction=result.direction.value,
                entry=float(result.entry),
                stop=float(result.stop),
                permission=perm,
                context_state=cs,
                validity=st.validity,
            )
        )

    print(f"[RC001-A] signals in eval window: {len(signals)}", flush=True)

    idx_1m_by_dt = {
        pd.Timestamp(frame_1m["dt_cst"].iloc[i]): i for i in range(len(frame_1m))
    }

    def run_arm(arm: str, use_filter: bool) -> tuple[list[Trade], list[dict]]:
        trades: list[Trade] = []
        decisions: list[dict] = []
        busy_until: pd.Timestamp | None = None
        for sig in signals:
            if busy_until is not None and sig.dt < busy_until:
                decisions.append(
                    {
                        "signal_dt": str(sig.dt),
                        "permission": sig.permission,
                        "action": "ignored_in_position",
                        "arm": arm,
                    }
                )
                continue
            if use_filter and sig.permission != "ALLOW":
                decisions.append(
                    {
                        "signal_dt": str(sig.dt),
                        "permission": sig.permission,
                        "action": "skip",
                        "context_state": sig.context_state,
                        "validity": sig.validity,
                        "arm": arm,
                    }
                )
                continue
            tr = _simulate_trade(
                arm=arm,
                sig=sig,
                frame_1m=frame_1m,
                idx_1m_by_dt=idx_1m_by_dt,
                frame_5m=frame_5m,
            )
            if tr is None:
                decisions.append(
                    {
                        "signal_dt": str(sig.dt),
                        "permission": sig.permission,
                        "action": "sim_fail",
                        "arm": arm,
                    }
                )
                continue
            trades.append(tr)
            busy_until = pd.Timestamp(tr.exit_dt)
            decisions.append(
                {
                    "signal_dt": str(sig.dt),
                    "permission": sig.permission if use_filter else "ALLOW",
                    "action": "enter",
                    "exit_reason": tr.exit_reason,
                    "pnl": tr.pnl,
                    "r": tr.r_multiple,
                    "arm": arm,
                }
            )
        return trades, decisions

    print("[RC001-A] simulate CTRL ...", flush=True)
    ctrl_trades, ctrl_dec = run_arm("CTRL", use_filter=False)
    print("[RC001-A] simulate FILT ...", flush=True)
    filt_trades, filt_dec = run_arm("FILT", use_filter=True)

    # E4 / A2: skipped FILT signals vs CTRL outcomes
    ctrl_by_dt = {t.signal_dt: t for t in ctrl_trades}
    skipped = [
        d
        for d in filt_dec
        if d.get("action") == "skip"
    ]
    skipped_ctrl_rs = [
        ctrl_by_dt[d["signal_dt"]].r_multiple
        for d in skipped
        if d["signal_dt"] in ctrl_by_dt
    ]
    # also counterfactual sim for skips not in CTRL due to position blocking
    for d in skipped:
        if d["signal_dt"] in ctrl_by_dt:
            continue
        # find signal object
        match = next((s for s in signals if str(s.dt) == d["signal_dt"]), None)
        if match is None:
            continue
        tr = _simulate_trade(
            arm="CF_SKIP",
            sig=match,
            frame_1m=frame_1m,
            idx_1m_by_dt=idx_1m_by_dt,
            frame_5m=frame_5m,
        )
        if tr is not None:
            skipped_ctrl_rs.append(tr.r_multiple)

    n_ctrl = len(ctrl_trades)
    n_filt = len(filt_trades)
    e1 = (n_filt / n_ctrl) if n_ctrl else float("nan")
    e2_ctrl = float(np.mean([t.r_multiple for t in ctrl_trades])) if ctrl_trades else float("nan")
    e2_filt = float(np.mean([t.r_multiple for t in filt_trades])) if filt_trades else float("nan")
    e3 = _max_dd([t.pnl for t in filt_trades]) - _max_dd([t.pnl for t in ctrl_trades])
    e4 = float(np.mean(skipped_ctrl_rs)) if skipped_ctrl_rs else float("nan")

    allow_n = sum(1 for s in signals if s.permission == "ALLOW")
    block_n = sum(1 for s in signals if s.permission == "BLOCK")
    mon_n = sum(1 for s in signals if s.permission == "MONITOR_ONLY")

    ctrl_rs = sorted([t.r_multiple for t in ctrl_trades], reverse=True)
    top_n = max(1, int(np.ceil(0.1 * len(ctrl_rs)))) if ctrl_rs else 0
    top_thresh = ctrl_rs[top_n - 1] if top_n else float("inf")
    top_ctrl = [t for t in ctrl_trades if t.r_multiple >= top_thresh]
    skipped_dts = {d["signal_dt"] for d in skipped}
    a2 = sum(1 for t in top_ctrl if t.signal_dt in skipped_dts)
    a2_den = len(top_ctrl) if top_ctrl else 0

    def _tail5(trades: list[Trade]) -> float:
        if not trades:
            return float("nan")
        arr = np.asarray([t.r_multiple for t in trades], dtype=float)
        return float(np.percentile(arr, 5))

    a3_delta = _tail5(filt_trades) - _tail5(ctrl_trades)

    s1 = sum(t.pnl for t in filt_trades) - sum(t.pnl for t in ctrl_trades)
    s2 = _sharpe([t.pnl for t in filt_trades]) - _sharpe([t.pnl for t in ctrl_trades])
    s3 = _pf([t.pnl for t in filt_trades]) - _pf([t.pnl for t in ctrl_trades])

    # Outcome rules (Spec §5.2)
    invalid = not integrity["pass"]
    outcome = "FAIL"
    if invalid:
        outcome = "INVALID"
    else:
        n_ok = n_ctrl >= 100
        e1_ok = 0.30 <= e1 <= 0.95 if np.isfinite(e1) else False
        e3_ok = e3 <= 0 if np.isfinite(e3) else False
        quality_ok = (
            (np.isfinite(e2_filt) and np.isfinite(e2_ctrl) and e2_filt >= e2_ctrl)
            or (np.isfinite(e4) and e4 <= 0)
        )
        a2_ratio = (a2 / a2_den) if a2_den else 0.0
        a2_ok = a2_ratio <= 0.50
        if (
            n_ok
            and n_filt >= 30
            and e1_ok
            and e3_ok
            and quality_ok
            and a2_ok
        ):
            outcome = "PASS"
        elif n_ok and e1 >= 0.15:
            partial = False
            if np.isfinite(e3) and e3 < 0:
                partial = True
            if e1_ok and np.isfinite(e4) and e4 <= 0:
                partial = True
            if n_filt >= 30 and np.isfinite(e2_filt) and np.isfinite(e2_ctrl) and e2_filt >= e2_ctrl:
                partial = True
            if partial and not (
                n_ok and n_filt >= 30 and e1_ok and e3_ok and quality_ok and a2_ok
            ):
                outcome = "PARTIAL"
            else:
                outcome = "FAIL"
        else:
            outcome = "FAIL"

    evaluation = {
        "schema": "RC001_A_EXP001_Evaluation_v1",
        "experiment_id": "RC001_A_EXP001",
        "run_id": "RC001_A_EXP001_RUN001",
        "outcome": outcome,
        "integrity": integrity,
        "primary": {
            "E1_trade_count_ratio": e1,
            "n_CTRL": n_ctrl,
            "n_FILT": n_filt,
            "E2_mean_R_CTRL": e2_ctrl,
            "E2_mean_R_FILT": e2_filt,
            "E3_maxDD_delta_FILT_minus_CTRL": e3,
            "E4_skipped_mean_R": e4,
            "n_skipped_with_R": len(skipped_ctrl_rs),
        },
        "attribution": {
            "A1_ALLOW": allow_n,
            "A1_BLOCK": block_n,
            "A1_MONITOR_ONLY": mon_n,
            "A2_missed_top_decile": a2,
            "A2_top_decile_n": a2_den,
            "A2_ratio": a2_ratio if a2_den else None,
            "A3_tail5_R_delta": a3_delta,
        },
        "secondary": {
            "S1_total_pnl_delta": s1,
            "S2_trade_sharpe_delta": s2,
            "S3_pf_delta": s3,
            "CTRL_total_pnl": sum(t.pnl for t in ctrl_trades),
            "FILT_total_pnl": sum(t.pnl for t in filt_trades),
        },
        "non_claims": [
            "not_alpha",
            "not_gate_pass",
            "not_rc001_accepted",
            "not_full_candidate",
            "rb_only_neq_multi_symbol",
            "fail_neq_k001_false",
        ],
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    evidence = {
        "schema": "RC001_A_EvidenceRecord_v1",
        "experiment_id": "RC001_A_EXP001",
        "run_id": "RC001_A_EXP001_RUN001",
        "outcome": outcome,
        "eq": "EQ-RC001-A-CONTEXT-FILTER-SELECTION",
        "filter_policy": FILTER_POLICY,
        "exit_family": EXIT_FAMILY,
        "baseline": "OPP16@1.0.0",
        "knowledge_action": "NONE",
        "affects": "Context Filter consumption evidence only",
        "evaluation_ref": "evaluation.json",
        "non_claims": evaluation["non_claims"],
        "lineage": {
            "opp16_sha256": integrity["opp16_sha256"],
            "dataset_fingerprints": integrity["dataset_fingerprints"],
            "code_revision": integrity["code_revision"],
            "spec": "docs/research/RC001_A_CONTROLLED_EXPERIMENT_SPEC.md",
            "confirmation": "docs/research/RC001_A_SPEC_CONFIRMATION.md",
            "execution_auth": "docs/research/RC001_A_EXECUTION_AUTHORIZATION.md",
        },
        "finished_at_utc": evaluation["finished_at_utc"],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    def _dump_trades(path: Path, trades: list[Trade]) -> None:
        rows = [asdict(t) for t in trades]
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _dump_trades(OUT_DIR / "trades_CTRL.json", ctrl_trades)
    _dump_trades(OUT_DIR / "trades_FILT.json", filt_trades)
    (OUT_DIR / "filter_decisions.json").write_text(
        json.dumps(filt_dec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT_DIR / "evaluation.json").write_text(
        json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT_DIR / "evidence_record.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "schema": "RC001_A_RunManifest_v1",
        "experiment_id": "RC001_A_EXP001",
        "run_id": "RC001_A_EXP001_RUN001",
        "outcome": outcome,
        "integrity": integrity,
        "reproduction_command": (
            ".\\\\.venv\\\\Scripts\\\\python.exe scripts\\\\run_rc001_a_exp001.py"
        ),
        "execution_authorized": True,
        "finished_at_utc": evaluation["finished_at_utc"],
    }
    (OUT_DIR / "RC001_A_EXP001_RUN_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"[RC001-A] outcome={outcome} n_CTRL={n_ctrl} n_FILT={n_filt} "
        f"E1={e1:.4f} E2c={e2_ctrl:.4f} E2f={e2_filt:.4f} E3={e3:.2f} E4={e4}",
        flush=True,
    )
    return 0 if outcome != "INVALID" else 1


if __name__ == "__main__":
    raise SystemExit(run())
