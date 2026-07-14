"""Scan all data/tq symbols for truncated / low-quality monthly contracts."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_rollover_map import SYMBOL_CONFIG  # noqa: E402
from tools.download_rb_monthly import (  # noqa: E402
    _build_contract_dates,
    _check_contract_quality,
    get_auth,
)

PREFIX_TO_SYMBOL = {
    cfg["prefix"]: f"{cfg['exchange']}.{cfg['prefix']}" for cfg in SYMBOL_CONFIG.values()
}

DATA = ROOT / "data" / "tq"


def main() -> None:
    auth = get_auth()
    issues: list[dict] = []
    ok_non_dom: list[tuple[str, str, int | None]] = []

    symbols = sorted(
        p.name for p in DATA.iterdir() if p.is_dir() and (p / "manifest.json").exists()
    )
    print(f"scanning {len(symbols)} symbols...")

    for prefix in symbols:
        symbol = PREFIX_TO_SYMBOL.get(prefix)
        if not symbol:
            print(f"  skip {prefix}: unknown symbol mapping")
            continue

        output_dir = str(DATA / prefix)
        manifest = json.loads((DATA / prefix / "manifest.json").read_text(encoding="utf-8"))
        dom_keys: set[str] = set()
        dw_path = DATA / prefix / "dominant_windows.json"
        if dw_path.exists():
            dom_keys = set(
                json.loads(dw_path.read_text(encoding="utf-8")).get("windows", {}).keys()
            )

        try:
            contracts = _build_contract_dates(symbol, 2021, 2026, auth)
        except Exception as exc:
            print(f"  skip {prefix}: {exc}")
            continue

        meta_by_file = {
            f"{prefix}_{meta['yymm']}.parquet": (sym, meta)
            for sym, meta in contracts.items()
        }

        for fname, entry in manifest.items():
            if fname.startswith("_") or not fname.endswith(".parquet"):
                continue
            if entry.get("skip_reason") == "no_data":
                continue
            yymm = fname.replace(f"{prefix}_", "").replace(".parquet", "")
            pair = meta_by_file.get(fname)
            if not pair:
                continue
            sym, meta = pair
            is_good, reason, _ = _check_contract_quality(
                sym, meta, output_dir, prefix, manifest_entry=entry, deep=True
            )
            in_dom = yymm in dom_keys
            if not is_good:
                issues.append(
                    {
                        "prefix": prefix,
                        "yymm": yymm,
                        "in_dom": in_dom,
                        "rows": entry.get("rows"),
                        "end": entry.get("end_date"),
                        "reason": reason,
                    }
                )
            elif not in_dom:
                ok_non_dom.append((prefix, yymm, entry.get("rows")))

    print(f"\n=== DEFECTS ({len(issues)}) ===")
    for x in sorted(issues, key=lambda z: (z["prefix"], z["yymm"])):
        dom = "dom" if x["in_dom"] else "non-dom"
        print(
            f"  {x['prefix']}_{x['yymm']} [{dom}] "
            f"rows={x['rows']} end={x['end']} -> {x['reason']}"
        )

    non_dom_defects = [x for x in issues if not x["in_dom"]]
    dom_defects = [x for x in issues if x["in_dom"]]
    print(f"\n  in dominant window: {len(dom_defects)}")
    print(f"  outside dominant window (hidden risk): {len(non_dom_defects)}")
    print(f"\n=== OK but outside dominant window: {len(ok_non_dom)} ===")

    # Tail-gap scan: actual end vs full-contract planned end (rb_2301 class)
    tail_gaps: list[dict] = []
    for prefix in symbols:
        symbol = PREFIX_TO_SYMBOL.get(prefix)
        if not symbol:
            continue
        output_dir = DATA / prefix
        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        dom_keys: set[str] = set()
        dw_path = output_dir / "dominant_windows.json"
        if dw_path.exists():
            dom_keys = set(
                json.loads(dw_path.read_text(encoding="utf-8")).get("windows", {}).keys()
            )
        try:
            contracts = _build_contract_dates(symbol, 2021, 2026, auth)
        except Exception:
            continue
        meta_by_yymm = {meta["yymm"]: meta for meta in contracts.values()}
        for fname, entry in manifest.items():
            if fname.startswith("_") or not fname.endswith(".parquet"):
                continue
            if entry.get("skip_reason") == "no_data":
                continue
            yymm = fname.replace(f"{prefix}_", "").replace(".parquet", "")
            meta = meta_by_yymm.get(yymm)
            m_end = entry.get("end_date")
            if not meta or not m_end:
                continue
            end_plan = datetime.strptime(meta["end_date"], "%Y-%m-%d") + timedelta(
                hours=23, minutes=59, seconds=59
            )
            dt_max = datetime.strptime(m_end, "%Y-%m-%d")
            gap_end = (end_plan - dt_max).total_seconds() / 86400.0
            if gap_end > 30:
                tail_gaps.append(
                    {
                        "prefix": prefix,
                        "yymm": yymm,
                        "gap_end": round(gap_end, 1),
                        "rows": entry.get("rows"),
                        "end": m_end,
                        "plan": meta["end_date"],
                        "in_dom": yymm in dom_keys,
                    }
                )

    print(f"\n=== TAIL GAP (end >30d before full-contract plan): {len(tail_gaps)} ===")
    for x in sorted(tail_gaps, key=lambda z: (z["prefix"], z["yymm"])):
        tag = "dom" if x["in_dom"] else "NON-DOM"
        print(
            f"  {x['prefix']}_{x['yymm']} [{tag}] "
            f"end={x['end']} plan={x['plan']} gap={x['gap_end']}d rows={x['rows']}"
        )
    hidden = [x for x in tail_gaps if not x["in_dom"]]
    print(f"  of which NON-DOM (hidden, rb_2301 class): {len(hidden)}")


if __name__ == "__main__":
    main()
