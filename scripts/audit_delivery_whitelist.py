"""Audit rollover chains vs SYMBOL_ALLOWED_DELIVERY_MONTHS for all symbols."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_rollover_map import SYMBOL_CONFIG  # noqa: E402
from tools.rollover_rules import (  # noqa: E402
    SYMBOL_ALLOWED_DELIVERY_MONTHS,
    allowed_months_for_symbol,
    delivery_month_from_yymm,
    resolve_rollover_symbol_key,
)

DATA = ROOT / "data" / "tq"
PREFIX_TO_KEY = {cfg["prefix"]: key for key, cfg in SYMBOL_CONFIG.items()}


def yymm_month(yymm: str) -> int:
    return delivery_month_from_yymm(yymm)


def audit_prefix(prefix: str) -> dict:
    key = PREFIX_TO_KEY.get(prefix) or resolve_rollover_symbol_key(prefix)
    if not key:
        return {"prefix": prefix, "status": "unknown_prefix"}

    allowed = allowed_months_for_symbol(key)
    rm_path = DATA / prefix / "rollover_map.parquet"
    if not rm_path.exists():
        return {"prefix": prefix, "key": key, "status": "no_rollover_map"}

    rm = pd.read_parquet(rm_path)
    contracts: set[str] = set()
    hops: list[str] = []

    if "from_yymm" in rm.columns:
        for _, row in rm.iterrows():
            fy, ty = str(row["from_yymm"]), str(row["to_yymm"])
            contracts.update({fy, ty})
            if len(fy) == 4 and int(fy[:2]) >= 21:
                hops.append(f"{fy}->{ty}")
    else:
        return {"prefix": prefix, "key": key, "status": "unexpected_columns", "cols": list(rm.columns)}

    recent = sorted(c for c in contracts if len(c) == 4 and c.isdigit() and int(c[:2]) >= 21)
    violations: list[tuple[str, int]] = []
    if allowed:
        for yymm in recent:
            m = yymm_month(yymm)
            if m not in allowed:
                violations.append((yymm, m))

    dw_path = DATA / prefix / "dominant_windows.json"
    dw_contracts: list[str] = []
    if dw_path.exists():
        dw = json.loads(dw_path.read_text(encoding="utf-8"))
        dw_contracts = sorted(
            k for k in dw.get("windows", {}) if len(k) == 4 and int(k[:2]) >= 21
        )

    dw_violations: list[tuple[str, int]] = []
    if allowed:
        for yymm in dw_contracts:
            m = yymm_month(yymm)
            if m not in allowed:
                dw_violations.append((yymm, m))

    return {
        "prefix": prefix,
        "key": key,
        "allowed": allowed,
        "violations": violations,
        "dw_violations": dw_violations,
        "chain_2021+": recent,
        "dw_2021+": dw_contracts,
        "hops_2021+": hops,
        "odd_hops": odd_hops(hops, allowed),
        "status": "ok" if not violations and not dw_violations else "mismatch",
    }


def hop_months(hop: str) -> tuple[int, int]:
    fy, ty = hop.split("->")
    return int(fy[2:4]), int(ty[2:4])


def odd_hops(hops: list[str], allowed: tuple[int, ...] | None) -> list[str]:
    """Flag hops that use non-allowed months (None whitelist: transitional even-month hops)."""
    odd: list[str] = []
    if allowed is not None:
        for h in hops:
            fm, tm = hop_months(h)
            if fm not in allowed or tm not in allowed:
                odd.append(h)
        return odd
    for h in hops:
        fm, tm = hop_months(h)
        gap = (tm - fm) % 12
        if gap not in (0, 1) and not (fm == 12 and tm == 1):
            odd.append(h)
    return odd


def main() -> None:
    symbols = sorted(
        p.name for p in DATA.iterdir() if p.is_dir() and (p / "manifest.json").exists()
    )
    mismatches: list[dict] = []
    odd_chain: list[dict] = []
    missing_map: list[str] = []
    ok_with_whitelist: list[str] = []
    ok_none: list[str] = []

    print(f"Auditing {len(symbols)} symbols...\n")

    for prefix in symbols:
        r = audit_prefix(prefix)
        st = r.get("status")
        if st == "no_rollover_map":
            missing_map.append(prefix)
            continue
        if st not in ("ok", "mismatch"):
            print(f"  {prefix}: {st}")
            continue
        if r["violations"] or r["dw_violations"]:
            mismatches.append(r)
        elif r.get("odd_hops"):
            odd_chain.append(r)
        elif r["allowed"] is not None:
            ok_with_whitelist.append(prefix)
        else:
            ok_none.append(prefix)

    if mismatches:
        print("=== MISMATCH (chain or dominant_windows violates whitelist) ===")
        for r in mismatches:
            print(f"\n{r['prefix']} ({r['key']}) allowed={r['allowed']}")
            if r["violations"]:
                print(f"  rollover_map violations: {r['violations']}")
            if r["dw_violations"]:
                print(f"  dominant_windows violations: {r['dw_violations']}")
            print(f"  hops 2021+: {r['hops_2021+']}")
            print(f"  dw contracts 2021+: {r['dw_2021+']}")

    if odd_chain:
        print("=== ODD HOPS (skip months within whitelist or transitional None) ===")
        for r in odd_chain:
            print(f"\n{r['prefix']} ({r['key']}) allowed={r['allowed']}")
            print(f"  odd: {r['odd_hops']}")
            print(f"  hops 2021+: {r['hops_2021+']}")

    if missing_map:
        print(f"\n=== NO rollover_map ({len(missing_map)}) ===")
        print(", ".join(missing_map))

    print(f"\n=== OK with whitelist ({len(ok_with_whitelist)}) ===")
    print(", ".join(ok_with_whitelist))

    print(f"\n=== OK None whitelist ({len(ok_none)}) ===")
    print(", ".join(ok_none))

    # Symbols in SYMBOL_CONFIG but missing from data
    data_prefixes = set(symbols)
    cfg_prefixes = {cfg["prefix"] for cfg in SYMBOL_CONFIG.values()}
    missing_data = sorted(cfg_prefixes - data_prefixes)
    if missing_data:
        print(f"\n=== SYMBOL_CONFIG but no data ({len(missing_data)}) ===")
        print(", ".join(missing_data))

    # Whitelist keys not in SYMBOL_CONFIG
    cfg_keys = set(SYMBOL_CONFIG.keys())
    orphan_whitelist = sorted(k for k in SYMBOL_ALLOWED_DELIVERY_MONTHS if k not in cfg_keys)
    if orphan_whitelist:
        print(f"\n=== Whitelist keys not in SYMBOL_CONFIG ===")
        print(", ".join(orphan_whitelist))

    sys.exit(1 if mismatches or odd_chain else 0)


if __name__ == "__main__":
    main()
