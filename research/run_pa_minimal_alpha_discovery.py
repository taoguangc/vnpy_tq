# -*- coding: utf-8 -*-
"""pa_minimal 稳定 Alpha：8 品种全 OPP shadow 候选数据集。

一次扫描 CROSS_SYMBOL_UNIVERSE，alpha_shadow_mode=True（不武装、不持仓抢占），
导出 per-symbol CSV + 合并池，并跑稳定性门禁报告。

用法::
  python -m research.run_pa_minimal_alpha_discovery
  python -m research.run_pa_minimal_alpha_discovery --symbols rb,hc
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.pa_minimal_alpha_validation import pick_top_promote, run_stability_screen
from research.pa_minimal_baseline import (
    ALPHA_SHADOW_OVERRIDES,
    ALPHA_SYMBOL_UNIVERSE,
    WINDOW_END,
    WINDOW_START,
    build_alpha_protocol_manifest,
)
from strategies.pa_cta.symbol_config import cross_symbol_list
from strategies.pa_minimal.backtest import run_minimal_backtest

OUT_DIR = ROOT / "research" / "output" / "alpha_discovery"


def _run_symbol(symbol: str, out_dir: Path, *, verbose: bool) -> pd.DataFrame:
    export_path = out_dir / f"shadow_candidates_{symbol.lower()}.csv"
    overrides = dict(ALPHA_SHADOW_OVERRIDES)
    overrides["candidate_export_path"] = str(export_path)
    bt = run_minimal_backtest(
        symbol=symbol,
        zero_cost=False,
        verbose=verbose,
        start=WINDOW_START,
        end=WINDOW_END,
        strategy_overrides=overrides,
    )
    rows = bt.get("candidate_records") or []
    df = pd.DataFrame(rows)
    if not df.empty and "symbol" in df.columns:
        df["symbol"] = df["symbol"].astype(str).str.lower()
    elif not df.empty:
        df["symbol"] = symbol.lower()
    funnel = bt.get("candidate_funnel") or {}
    print(
        f"[{symbol}] candidates={funnel.get('candidates', len(df))} "
        f"gate_pass={funnel.get('gate_pass')} armed={funnel.get('armed')} "
        f"export={export_path.name}"
    )
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="pa_minimal alpha shadow discovery")
    parser.add_argument(
        "--symbols",
        default="",
        help="逗号分隔品种，默认 ALPHA_SYMBOL_UNIVERSE / CROSS_SYMBOL_UNIVERSE",
    )
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="只生成数据集，不跑稳定性门禁",
    )
    args = parser.parse_args()

    if args.symbols.strip():
        symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = [s for s in ALPHA_SYMBOL_UNIVERSE if s in set(cross_symbol_list())]

    out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_alpha_protocol_manifest(ROOT)
    (out_dir / "alpha_protocol_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"protocol={manifest['version']} opp_fp={manifest['opp_code_fingerprint']}")
    print(f"symbols={symbols}")

    frames: list[pd.DataFrame] = []
    errors: list[dict] = []
    for sym in symbols:
        try:
            df = _run_symbol(sym, out_dir, verbose=not args.quiet)
            if not df.empty:
                frames.append(df)
        except Exception as exc:
            errors.append({"symbol": sym, "error": str(exc), "trace": traceback.format_exc()})
            print(f"[{sym}] ERROR: {exc}")

    if not frames:
        print("无候选数据，中止。")
        (out_dir / "errors.json").write_text(
            json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return

    pooled = pd.concat(frames, ignore_index=True)
    pooled_path = out_dir / "shadow_candidates_all.csv"
    pooled.to_csv(pooled_path, index=False, encoding="utf-8-sig")
    print(f"\npooled n={len(pooled)} -> {pooled_path}")

    summary = {
        "n_total": int(len(pooled)),
        "n_gate_pass": int(pooled["gate_pass"].astype(bool).sum())
        if "gate_pass" in pooled.columns
        else 0,
        "by_symbol": pooled.groupby("symbol").size().to_dict() if "symbol" in pooled.columns else {},
        "by_setup": pooled.groupby("setup").size().to_dict() if "setup" in pooled.columns else {},
        "errors": errors,
        "protocol": manifest["version"],
        "opp_code_fingerprint": manifest["opp_code_fingerprint"],
    }
    (out_dir / "discovery_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    if args.skip_validate:
        return

    report = run_stability_screen(pooled, gate_pass_only=True)
    report_path = out_dir / "stability_report.csv"
    report.to_csv(report_path, index=False, encoding="utf-8-sig")
    print(f"\n===== 稳定性报告 ({report_path.name}) =====")
    if report.empty:
        print("无切片可评。")
        return
    show = report[
        [
            "opp_family",
            "direction",
            "label",
            "n",
            "n_symbols",
            "mean_net_r",
            "bootstrap_lb",
            "fold_pos_ratio",
            "loso_nonneg",
            "reasons",
        ]
    ]
    print(show.to_string(index=False))
    top = pick_top_promote(report)
    if top:
        print(f"\nTOP PROMOTE_TO_CTA: {top}")
        (out_dir / "top_promote.json").write_text(
            json.dumps(top, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    else:
        print("\n无 PROMOTE_TO_CTA；最高档见报告（PROVISIONAL/REJECT）。")
        (out_dir / "top_promote.json").write_text("null\n", encoding="utf-8")


if __name__ == "__main__":
    main()
