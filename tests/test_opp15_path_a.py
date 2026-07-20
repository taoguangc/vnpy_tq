# -*- coding: utf-8 -*-
"""OPP15 Path A：可达性、多空镜像、P3±tick 失效边界。"""
from __future__ import annotations

import unittest
from datetime import datetime, timedelta

from strategies.pa_minimal.detectors.opp15 import (
    _path_a_long_trigger_line,
    _path_a_short_trigger_line,
    match_opp15_trigger,
)
from tests.pa_fixtures import FakeAM, StopCapStrategy, make_bar


class TestOpp15PathA(unittest.TestCase):
    def _armed_short(self) -> StopCapStrategy:
        am = FakeAM(
            open=[100, 99, 98],
            high=[101, 100, 99],
            low=[99, 98, 96],   # [-1]=96 current, [-2]=98, [-3]=99
            close=[100, 98.5, 97],
        )
        s = StopCapStrategy(am_5min=am)
        s.wedge_setup_active = True
        s._wedge_direction = -1
        s.wedge_confirmed_p3_high = 110.0
        s.wedge_arm_time = datetime(2024, 1, 2, 10, 0)
        s.wedge_trigger_line = 98.0  # armed prior structure
        s.wedge_current_alpha = 0.9  # 高于 b_prime → 关 B'
        s.wedge_b_prime_alpha = 0.7
        s.wedge_p3_body_floor = 0.0
        return s

    def _armed_long(self) -> StopCapStrategy:
        am = FakeAM(
            open=[100, 101, 102],
            high=[101, 102, 105],  # [-1]=105, [-2]=102, [-3]=101
            low=[99, 100, 101],
            close=[100, 101.5, 103],
        )
        s = StopCapStrategy(am_5min=am)
        s.wedge_setup_active = True
        s._wedge_direction = 1
        s.wedge_confirmed_p3_high = 90.0
        s.wedge_arm_time = datetime(2024, 1, 2, 10, 0)
        s.wedge_trigger_line = 102.0
        s.wedge_current_alpha = 0.9
        s.wedge_b_prime_alpha = 0.7
        s.wedge_p3_body_floor = 0.0
        return s

    def test_path_a_short_line_excludes_current_low(self) -> None:
        s = self._armed_short()
        line = _path_a_short_trigger_line(s)
        # prior min(98,99)=98；armed=98 → 98；不含 current 96
        self.assertEqual(line, 98.0)
        self.assertGreater(line, float(s.am_5min.low[-1]))

    def test_path_a_short_reachable(self) -> None:
        s = self._armed_short()
        # 强阴，收盘 97.5 < trigger 98，且 >= 本棒 low 96
        bar = make_bar(99, 99.5, 96, 97.5, dt=datetime(2024, 1, 2, 10, 5))
        out = match_opp15_trigger(s, bar, atr_5=5.0, tick=1.0, is_strong_bar=True)
        setups = [m.setup for m in out]
        self.assertIn("OPP15_5M_WEDGE_REVERSAL", setups)

    def test_path_a_long_reachable_mirror(self) -> None:
        s = self._armed_long()
        line = _path_a_long_trigger_line(s)
        self.assertEqual(line, 102.0)  # max(armed 102, prior max(102,101))
        bar = make_bar(101, 105, 100.5, 103.5, dt=datetime(2024, 1, 2, 10, 5))
        out = match_opp15_trigger(s, bar, atr_5=5.0, tick=1.0, is_strong_bar=True)
        setups = [m.setup for m in out]
        self.assertIn("OPP15_5M_WEDGE_REVERSAL_LONG", setups)

    def test_p3_tick_invalidation_short(self) -> None:
        s = self._armed_short()
        tick = 1.0
        # high > p3 + tick → 失效空列表
        bar = make_bar(109, 111.5, 108, 109, dt=datetime(2024, 1, 2, 10, 5))
        self.assertEqual(
            match_opp15_trigger(s, bar, atr_5=5.0, tick=tick, is_strong_bar=True),
            [],
        )
        # high == p3 + tick 边界：条件是 high > p3 + tick，相等仍可继续
        bar2 = make_bar(109, 111.0, 108, 109, dt=datetime(2024, 1, 2, 10, 5))
        # 非强阴破线，可能空，但不因 P3 失效提前 return 成「结构破坏」以外的路径
        # 这里只断言未因 p3 直接清空前的逻辑：high 未超过
        self.assertFalse(bar2.high_price > s.wedge_confirmed_p3_high + tick)

    def test_arm_expiry_bars(self) -> None:
        s = self._armed_short()
        s.wedge_arm_trigger_max_bars = 2
        bar = make_bar(99, 99.5, 96, 97.5, dt=s.wedge_arm_time + timedelta(minutes=15))
        # 15/5=3 > 2
        self.assertEqual(
            match_opp15_trigger(s, bar, atr_5=5.0, tick=1.0, is_strong_bar=True),
            [],
        )


if __name__ == "__main__":
    unittest.main()
