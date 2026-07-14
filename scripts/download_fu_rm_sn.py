# -*- coding: utf-8 -*-
"""串行两阶段下载 fu / RM(菜粕) / sn，落盘 data/tq/{prefix}/。

用法::
  .venv/Scripts/python.exe scripts/download_fu_rm_sn.py
  .venv/Scripts/python.exe scripts/download_fu_rm_sn.py --from RM
  .venv/Scripts/python.exe scripts/download_fu_rm_sn.py --fu-1m-only
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"
DL = ROOT / "tools" / "download_rb_monthly.py"

# 菜粕是郑商所 CZCE.RM；DCE.rm 在 TQ 不存在（勿用 SYMBOL_CONFIG 的小写 rm）
JOBS: list[tuple[str, str, list[str]]] = [
    ("SHFE.fu", "fu", []),
    ("CZCE.RM", "RM", []),
    ("SHFE.sn", "sn", []),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from",
        dest="from_prefix",
        default=None,
        help="从指定品种续跑，如 RM / sn",
    )
    parser.add_argument(
        "--fu-1m-only",
        action="store_true",
        help="仅跑 fu Phase-2 1m（OI/建图已完成时），再继续 RM/sn",
    )
    parser.add_argument("-y", "--years", nargs=2, default=["2021", "2026"])
    args = parser.parse_args()

    if args.fu_1m_only:
        jobs: list[tuple[str, str, list[str]]] = [
            ("SHFE.fu", "fu", ["--phase", "1m"]),
            ("CZCE.RM", "RM", []),
            ("SHFE.sn", "sn", []),
        ]
    else:
        jobs = list(JOBS)

    if args.from_prefix:
        key = args.from_prefix.lower()
        idx = next(
            (i for i, (_, p, _) in enumerate(jobs) if p.lower() == key),
            None,
        )
        if idx is None:
            print(f"未知 --from {args.from_prefix}", file=sys.stderr)
            return 2
        jobs = jobs[idx:]

    log = ROOT / "data" / "tq" / "_download_fu_RM_sn.log"
    log.parent.mkdir(parents=True, exist_ok=True)

    for i, (tq_sym, prefix, extra) in enumerate(jobs, 1):
        bar = "=" * 72
        msg = (
            f"\n{bar}\n[{i}/{len(jobs)}] 下载 {tq_sym} → data/tq/{prefix}/ "
            f"extra={extra}\n{bar}\n"
        )
        print(msg, flush=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(msg)
        cmd = [
            str(PY),
            "-u",
            str(DL),
            "-s",
            tq_sym,
            "-y",
            args.years[0],
            args.years[1],
            *extra,
        ]
        print(" ".join(cmd), flush=True)
        with log.open("a", encoding="utf-8") as fh:
            rc = subprocess.call(cmd, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT)
        if rc != 0:
            print(f"FAIL {tq_sym} exit={rc}", file=sys.stderr, flush=True)
            return rc
        print(f"OK {tq_sym}", flush=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"OK {tq_sym}\n")

    print("\n全部完成:", [p for _, p, _ in jobs], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
