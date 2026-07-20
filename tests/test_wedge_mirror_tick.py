# -*- coding: utf-8 -*-
"""楔形引擎：多空镜像 + tick 地板边界。"""
from __future__ import annotations

import unittest

from strategies.pa_cta.wedge import (
    WedgeBar,
    _evaluate_hh3_triple,
    _evaluate_ll3_triple,
    is_1bar_swing_high,
    is_1bar_swing_low,
    is_2bar_fractal_high,
    is_2bar_fractal_low,
    scan_latest_bearish_wedge,
    scan_latest_bullish_wedge,
)
from tests.pa_fixtures import mirror_wedge_bars, wb


def _ll3_fixture_bars() -> list[WedgeBar]:
    """手工构造可通过审计的 LL3（含确认棒）。

    P1/P2/P3 低点 100→90→83（move1=10, move2=7, alpha=0.7）；
    反弹峰递减约 112→102。
    """
    rows = [
        (105, 106, 104, 105),  # 0
        (105, 107, 104, 106),  # 1
        (106, 108, 105, 107),  # 2
        (107, 109, 106, 108),  # 3
        # 4 = P1 fractal low 100
        (104, 105, 100, 101),
        (101, 102, 100.5, 101.5),  # 5
        (101.5, 112, 101, 111),    # 6 peak1 ~112
        (111, 113, 110, 112),      # 7
        (112, 114, 111, 113),      # 8
        (113, 115, 112, 114),      # 9
        # 10 = P2 fractal low 90
        (108, 109, 90, 91),
        (91, 92, 90.5, 91.5),      # 11
        (91.5, 102, 91, 101),      # 12 peak2 ~102
        (101, 103, 100, 102),      # 13
        (102, 104, 101, 103),      # 14
        (103, 105, 102, 104),      # 15
        # 16 = P3 fractal low 83
        (98, 99, 83, 84),
        (84, 85, 83.5, 84.5),      # 17
        (84.5, 92, 84, 91),        # 18
        (91, 93, 90, 92),          # 19
        (92, 94, 91, 93),          # 20
    ]
    return [wb(o, h, l, c, i) for i, (o, h, l, c) in enumerate(rows)]


class TestWedgeMirror(unittest.TestCase):
    def test_fractal_low_high_mirror(self) -> None:
        bars = _ll3_fixture_bars()
        mir = mirror_wedge_bars(bars)
        for i in range(2, len(bars) - 2):
            self.assertEqual(
                is_2bar_fractal_low(bars, i),
                is_2bar_fractal_high(mir, i),
                msg=f"fractal mirror fail at {i}",
            )

    def test_1bar_swing_mirror(self) -> None:
        bars = _ll3_fixture_bars()
        mir = mirror_wedge_bars(bars)
        for i in range(1, len(bars) - 1):
            self.assertEqual(
                is_1bar_swing_low(bars, i),
                is_1bar_swing_high(mir, i),
                msg=f"1bar swing mirror fail at {i}",
            )

    def test_ll3_hh3_evaluate_mirror(self) -> None:
        bars = _ll3_fixture_bars()
        p1, p2, p3 = bars[4], bars[10], bars[16]
        atr, tick = 10.0, 1.0
        bull = _evaluate_ll3_triple(
            bars, p1, p2, p3, atr_5=atr, tick_size=tick, n_min=3, alpha_threshold=0.85,
        )
        self.assertEqual(bull.get("status"), "wedge_valid:ll3", bull)

        mir = mirror_wedge_bars(bars)
        bear = _evaluate_hh3_triple(
            mir, mir[4], mir[10], mir[16],
            atr_5=atr, tick_size=tick, n_min=3, alpha_threshold=0.85,
        )
        self.assertEqual(bear.get("status"), "wedge_valid:hh3", bear)
        self.assertAlmostEqual(float(bull["alpha"]), float(bear["alpha"]), places=6)
        self.assertEqual(bull["p1_idx"], bear["p1_idx"])
        self.assertEqual(bull["p3_idx"], bear["p3_idx"])

    def test_scan_latest_mirror(self) -> None:
        bars = _ll3_fixture_bars()
        atr, tick = 10.0, 1.0
        bull = scan_latest_bullish_wedge(bars, atr, tick_size=tick, n_min=3)
        self.assertEqual(bull.get("status"), "wedge_valid:ll3", bull)
        mir = mirror_wedge_bars(bars)
        bear = scan_latest_bearish_wedge(mir, atr, tick_size=tick, n_min=3)
        self.assertEqual(bear.get("status"), "wedge_valid:hh3", bear)
        self.assertEqual(bull["p1_idx"], bear["p1_idx"])
        self.assertEqual(bull["p2_idx"], bear["p2_idx"])
        self.assertEqual(bull["p3_idx"], bear["p3_idx"])
        self.assertAlmostEqual(float(bull["alpha"]), float(bear["alpha"]), places=6)

    def test_move_floor_tick_boundary(self) -> None:
        """tick 放大使 move1 < 3*tick → move_floor；正常 tick 可通过。"""
        bars = _ll3_fixture_bars()
        p1, p2, p3 = bars[4], bars[10], bars[16]
        # move1=10, move2=7；tick=4 → 3*tick=12 > 10
        bad = _evaluate_ll3_triple(
            bars, p1, p2, p3, atr_5=1.0, tick_size=4.0, n_min=3, alpha_threshold=0.85,
        )
        self.assertEqual(bad.get("status"), "wedge_invalid:move_floor", bad)
        ok = _evaluate_ll3_triple(
            bars, p1, p2, p3, atr_5=10.0, tick_size=1.0, n_min=3, alpha_threshold=0.85,
        )
        self.assertEqual(ok.get("status"), "wedge_valid:ll3", ok)


if __name__ == "__main__":
    unittest.main()
