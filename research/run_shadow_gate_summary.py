# -*- coding: utf-8
"""EXP-027 — Production OPP 影子账本 gate 分解汇总。

读取 ``shadow_ledger_{symbol}.csv``，输出 disposition / gate / setup 三层期望分解，
并写入 ``research/output/shadow_gate_*_{symbol}.csv``。

用法::
  python -m research.run_shadow_gate_summary --symbol rb
  python -m research.run_shadow_gate_summary --input research/output/shadow_ledger_rb.csv
  python -m research.run_shadow_gate_summary --symbol rb --run-ledger
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FWD_COL = "fwd_120m_yuan"
EOD_COL = "eod_yuan_net"
DISPOSITION_ORDER = ("TRADED", "ARMED", "GATE_BLOCKED", "PREEMPTED", "POS_SKIP", "GLOBAL_SKIP")


def _mean_pct(series: pd.Series) -> float:
    if series.empty:
        return float("nan")
    return float(series.mean())


def _hit1r_pct(series: pd.Series) -> float:
    if series.empty:
        return float("nan")
    return float(series.mean() * 100.0)


def summarize_by_source(df: pd.DataFrame) -> pd.DataFrame:
    if "source" not in df.columns:
        return pd.DataFrame(columns=["source", "n", "fwd120_mean"])
    rows = []
    for src, sub in df.groupby("source"):
        rows.append({
            "source": src,
            "n": len(sub),
            "fwd120_mean": round(_mean_pct(sub[FWD_COL]), 1),
            "eod_net_mean": round(_mean_pct(sub[EOD_COL]), 1),
            "preempted_n": int((sub["disposition"] == "PREEMPTED").sum()),
            "global_skip_n": int((sub["disposition"] == "GLOBAL_SKIP").sum()),
        })
    return pd.DataFrame(rows)


def summarize_preempted(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[df["disposition"] == "PREEMPTED"]
    if sub.empty:
        return pd.DataFrame(columns=["preempted_by", "n", "fwd120_mean"])
    rows = []
    for by, g in sub.groupby("preempted_by", dropna=False):
        rows.append({
            "preempted_by": by if pd.notna(by) else "(unknown)",
            "n": len(g),
            "fwd120_mean": round(_mean_pct(g[FWD_COL]), 1),
            "eod_net_mean": round(_mean_pct(g[EOD_COL]), 1),
            "top_setup": g["setup"].mode().iloc[0] if not g["setup"].mode().empty else "",
        })
    return pd.DataFrame(rows).sort_values("n", ascending=False).reset_index(drop=True)


def summarize_by_disposition(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for disp in DISPOSITION_ORDER:
        sub = df[df["disposition"] == disp]
        if sub.empty:
            continue
        rows.append(
            {
                "segment": disp,
                "n": len(sub),
                "pct": round(len(sub) / len(df) * 100.0, 1),
                "fwd120_mean": round(_mean_pct(sub[FWD_COL]), 1),
                "fwd120_median": round(float(sub[FWD_COL].median()), 1),
                "eod_net_mean": round(_mean_pct(sub[EOD_COL]), 1),
                "mfe_mean": round(_mean_pct(sub["mfe_yuan"]), 1),
                "mae_mean": round(_mean_pct(sub["mae_yuan"]), 1),
                "hit_1r_pct": round(_hit1r_pct(sub["hit_1r"]), 1),
                "traded_n": int(sub["traded"].sum()),
            }
        )
    all_row = {
        "segment": "ALL",
        "n": len(df),
        "pct": 100.0,
        "fwd120_mean": round(_mean_pct(df[FWD_COL]), 1),
        "fwd120_median": round(float(df[FWD_COL].median()), 1),
        "eod_net_mean": round(_mean_pct(df[EOD_COL]), 1),
        "mfe_mean": round(_mean_pct(df["mfe_yuan"]), 1),
        "mae_mean": round(_mean_pct(df["mae_yuan"]), 1),
        "hit_1r_pct": round(_hit1r_pct(df["hit_1r"]), 1),
        "traded_n": int(df["traded"].sum()),
    }
    return pd.DataFrame(rows + [all_row])


def summarize_gate_blocks(df: pd.DataFrame) -> pd.DataFrame:
    blocked = df[df["disposition"] == "GATE_BLOCKED"].copy()
    if blocked.empty:
        return pd.DataFrame(
            columns=[
                "first_blocking_gate",
                "n",
                "pct_of_blocked",
                "fwd120_mean",
                "eod_net_mean",
                "hit_1r_pct",
            ]
        )
    total = len(blocked)
    rows: list[dict] = []
    for gate, sub in blocked.groupby("first_blocking_gate", dropna=False):
        label = gate if pd.notna(gate) and str(gate).strip() else "(unknown)"
        rows.append(
            {
                "first_blocking_gate": label,
                "n": len(sub),
                "pct_of_blocked": round(len(sub) / total * 100.0, 1),
                "fwd120_mean": round(_mean_pct(sub[FWD_COL]), 1),
                "eod_net_mean": round(_mean_pct(sub[EOD_COL]), 1),
                "hit_1r_pct": round(_hit1r_pct(sub["hit_1r"]), 1),
            }
        )
    out = pd.DataFrame(rows).sort_values("n", ascending=False)
    return out.reset_index(drop=True)


def summarize_by_setup(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for setup, sub in df.groupby("setup", sort=True):
        traded = sub[sub["disposition"] == "TRADED"]
        blocked = sub[sub["disposition"] == "GATE_BLOCKED"]
        armed = sub[sub["disposition"] == "ARMED"]
        rows.append(
            {
                "setup": setup,
                "n": len(sub),
                "traded": len(traded),
                "armed_only": len(armed),
                "gate_blocked": len(blocked),
                "preempted": int((sub["disposition"] == "PREEMPTED").sum()),
                "fwd120_all": round(_mean_pct(sub[FWD_COL]), 1),
                "fwd120_traded": round(_mean_pct(traded[FWD_COL]), 1) if len(traded) else np.nan,
                "fwd120_armed": round(_mean_pct(armed[FWD_COL]), 1) if len(armed) else np.nan,
                "fwd120_blocked": round(_mean_pct(blocked[FWD_COL]), 1) if len(blocked) else np.nan,
                "hit_1r_all_pct": round(_hit1r_pct(sub["hit_1r"]), 1),
                "top_block_gate": (
                    blocked["first_blocking_gate"].mode().iloc[0]
                    if len(blocked) and not blocked["first_blocking_gate"].mode().empty
                    else ""
                ),
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values(["traded", "fwd120_traded"], ascending=[False, False]).reset_index(drop=True)


def summarize_setup_disposition(df: pd.DataFrame) -> pd.DataFrame:
    ct = pd.crosstab(df["setup"], df["disposition"])
    for col in DISPOSITION_ORDER:
        if col not in ct.columns:
            ct[col] = 0
    cols = [c for c in DISPOSITION_ORDER if c in ct.columns]
    extra = [c for c in ct.columns if c not in cols]
    return ct[cols + extra].sort_index()


def decomposition_chain(df: pd.DataFrame) -> pd.DataFrame:
    """信号 → gate → confirm 三段 fwd120 均值（聚合）。"""
    traded = df[df["disposition"] == "TRADED"]
    blocked = df[df["disposition"] == "GATE_BLOCKED"]
    armed = df[df["disposition"] == "ARMED"]
    segments = [
        ("1_raw_all", df),
        ("2_gate_blocked", blocked),
        ("3_armed_not_traded", armed),
        ("4_traded", traded),
    ]
    rows = []
    for label, sub in segments:
        rows.append(
            {
                "layer": label,
                "n": len(sub),
                "fwd120_mean": round(_mean_pct(sub[FWD_COL]), 1),
                "eod_net_mean": round(_mean_pct(sub[EOD_COL]), 1),
                "hit_1r_pct": round(_hit1r_pct(sub["hit_1r"]), 1),
            }
        )
    return pd.DataFrame(rows)


def print_report(
    df: pd.DataFrame,
    *,
    symbol: str,
    source: Path,
) -> None:
    disp = summarize_by_disposition(df)
    gates = summarize_gate_blocks(df)
    setup = summarize_by_setup(df)
    chain = decomposition_chain(df)
    by_source = summarize_by_source(df)
    preempt = summarize_preempted(df)

    print(f"\n=== EXP-027 Gate 分解 | {symbol} | {source.name} ===")
    print(f"候选数: {len(df):,}  |  成交: {int(df['traded'].sum()):,}")

    print("\n--- disposition ---")
    print(
        disp.to_string(
            index=False,
            formatters={
                "fwd120_mean": lambda x: f"{x:+.1f}" if pd.notna(x) else "nan",
                "eod_net_mean": lambda x: f"{x:+.1f}" if pd.notna(x) else "nan",
            },
        )
    )

    print("\n--- source (ARM vs DRY_SCAN) ---")
    if by_source.empty:
        print("  (无 source 列)")
    else:
        print(by_source.to_string(index=False))

    print("\n--- gate 拦截 (GATE_BLOCKED) ---")
    if gates.empty:
        print("  (无)")
    else:
        print(gates.to_string(index=False))

    print("\n--- PREEMPTED by ---")
    if preempt.empty:
        print("  (无)")
    else:
        print(preempt.head(15).to_string(index=False))

    print("\n--- 分解链 fwd120 ---")
    print(chain.to_string(index=False))

    print("\n--- setup（按 traded fwd120 降序，前 10）---")
    top = setup[setup["traded"] > 0].head(10)
    if top.empty:
        print("  (无成交 setup)")
    else:
        print(top.to_string(index=False, na_rep="—"))


def export_summaries(
    df: pd.DataFrame,
    *,
    symbol: str,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    tables = {
        f"shadow_gate_disposition_{symbol}.csv": summarize_by_disposition(df),
        f"shadow_gate_blocks_{symbol}.csv": summarize_gate_blocks(df),
        f"shadow_gate_setup_{symbol}.csv": summarize_by_setup(df),
        f"shadow_gate_setup_disp_{symbol}.csv": summarize_setup_disposition(df),
        f"shadow_gate_chain_{symbol}.csv": decomposition_chain(df),
        f"shadow_gate_source_{symbol}.csv": summarize_by_source(df),
        f"shadow_gate_preempted_{symbol}.csv": summarize_preempted(df),
    }
    for name, table in tables.items():
        path = output_dir / name
        table.to_csv(path, index=False, encoding="utf-8")
        paths[name] = path
    return paths


def load_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"未找到影子账本: {path}（先跑 run_shadow_ledger）")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"影子账本为空: {path}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Production OPP 影子账本 gate 分解汇总")
    parser.add_argument("--symbol", default="rb", help="品种（默认 rb）")
    parser.add_argument(
        "--input",
        default=None,
        help="影子账本 CSV（默认 research/output/shadow_ledger_{symbol}.csv）",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "research" / "output"),
        help="汇总 CSV 输出目录",
    )
    parser.add_argument(
        "--run-ledger",
        action="store_true",
        help="先跑 shadow ledger 回测再汇总",
    )
    parser.add_argument("--zero-cost", action="store_true", help="配合 --run-ledger")
    args = parser.parse_args()

    symbol = args.symbol.lower()
    ledger_path = Path(args.input) if args.input else ROOT / "research" / "output" / f"shadow_ledger_{symbol}.csv"

    if args.run_ledger:
        from strategies.pa_cta.backtest import run_parquet_backtest

        print(f"=== 运行影子账本回测 | {symbol} ===")
        run_parquet_backtest(
            symbol=symbol,
            zero_cost=args.zero_cost,
            verbose=True,
            strategy_overrides={"shadow_ledger_enabled": True},
        )

    df = load_ledger(ledger_path)
    sym = str(df["symbol"].iloc[0]) if "symbol" in df.columns and len(df) else symbol
    print_report(df, symbol=sym, source=ledger_path)

    out_dir = Path(args.output_dir)
    paths = export_summaries(df, symbol=sym, output_dir=out_dir)
    print("\n--- 导出 ---")
    for name, path in paths.items():
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
