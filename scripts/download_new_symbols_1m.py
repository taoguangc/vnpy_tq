# -*- coding: utf-8
"""串行下载 al/zn/y/p/l/FG 分月 1m，并重建换月表。

用法::
  .venv/Scripts/python.exe scripts/download_new_symbols_1m.py
  .venv/Scripts/python.exe scripts/download_new_symbols_1m.py --from y
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"
DL = ROOT / "tools" / "download_rb_monthly.py"

JOBS: list[tuple[str, str]] = [
    ("SHFE.al", "al"),
    ("SHFE.zn", "zn"),
    ("DCE.y", "y"),
    ("DCE.p", "p"),
    ("DCE.l", "l"),
    ("CZCE.FG", "FG"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from",
        dest="from_prefix",
        default=None,
        help="从指定品种续跑，如 y / p / FG",
    )
    args = parser.parse_args()
    years = ["2020", "2026"]
    jobs = JOBS
    if args.from_prefix:
        key = args.from_prefix.lower()
        idx = next(
            (i for i, (_, p) in enumerate(JOBS) if p.lower() == key),
            None,
        )
        if idx is None:
            print(f"未知 --from {args.from_prefix}", file=sys.stderr)
            return 2
        jobs = JOBS[idx:]

    log = ROOT / "data" / "tq" / "_download_al_zn_y_p_l_FG.log"
    log.parent.mkdir(parents=True, exist_ok=True)

    for i, (tq_sym, prefix) in enumerate(jobs, 1):
        msg = f"\n{'=' * 72}\n[{i}/{len(jobs)}] 下载 {tq_sym} → data/tq/{prefix}/\n{'=' * 72}\n"
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
            *years,
            "--rebuild-continuous",
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
    print("\n全部完成:", [p for _, p in jobs], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
