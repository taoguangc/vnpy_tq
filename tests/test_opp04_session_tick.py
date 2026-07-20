# -*- coding: utf-8 -*-
"""OPP04：跨时段、消费标志、回调趋势线 tick 边界。"""
from __future__ import annotations

import unittest
from datetime import datetime

from strategies.pa_minimal.detectors.opp04 import (
    _pullback_tl_breakout_long,
    _tl_price_at,
    match_opp04,
    note_opp04_consumed,
    opp04_session_key,
    roll_opp04_session,
)
from tests.pa_fixtures import FakeAM, StopCapStrategy, make_bar
from tests.test_wedge_mirror_tick import _ll3_fixture_bars


def _am_from_wedge_fixture() -> FakeAM:
    bars = _ll3_fixture_bars()
    return FakeAM(
        open=[b.open_price for b in bars],
        high=[b.high_price for b in bars],
        low=[b.low_price for b in bars],
        close=[b.close_price for b in bars],
    )


class TestOpp04SessionTick(unittest.TestCase):
    def test_session_key_day_vs_night(self) -> None:
        self.assertTrue(opp04_session_key(datetime(2024, 1, 2, 10, 0)).endswith("-D"))
        self.assertTrue(opp04_session_key(datetime(2024, 1, 2, 21, 5)).endswith("-N"))
        self.assertTrue(opp04_session_key(datetime(2024, 1, 3, 1, 0)).endswith("-N"))

    def test_roll_clears_consumed_across_session(self) -> None:
        s = StopCapStrategy()
        s._opp04_consumed = {("x",)}
        day = make_bar(100, 101, 99, 100, dt=datetime(2024, 1, 2, 10, 0))
        roll_opp04_session(s, day)
        self.assertEqual(s._opp04_bars_in_session, 1)
        s._opp04_consumed.add(("keep",))
        night = make_bar(100, 101, 99, 100, dt=datetime(2024, 1, 2, 21, 5))
        roll_opp04_session(s, night)
        self.assertEqual(s._opp04_consumed, set())
        self.assertEqual(s._opp04_bars_in_session, 1)

    def test_p3_max_age_blocks_stale_wedge(self) -> None:
        am = _am_from_wedge_fixture()
        s = StopCapStrategy(am_5min=am, always_in="LONG", trend_phase="EARLY")
        s.wedge_flag_p3_max_age = 2  # P3 在 idx16，当前 20 → age=4 > 2
        s.wedge_flag_require_tl_break = False
        # 预热时段计数，避免 session_bound 误杀
        for i in range(30):
            roll_opp04_session(s, make_bar(1, 1, 1, 1, dt=datetime(2024, 1, 2, 10, i % 60)))
        bar = make_bar(92, 98, 91, 97, dt=datetime(2024, 1, 2, 10, 30))
        out = match_opp04(s, bar, "STRONG_BULL", atr_5=10.0, tick=1.0, stop_buffer=1.0)
        self.assertEqual(out, [])

    def test_consume_prevents_rearm(self) -> None:
        am = _am_from_wedge_fixture()
        s = StopCapStrategy(am_5min=am, always_in="LONG", trend_phase="EARLY")
        s.wedge_flag_require_tl_break = False
        s.wedge_flag_p3_max_age = 20
        for _ in range(25):
            roll_opp04_session(s, make_bar(1, 1, 1, 1, dt=datetime(2024, 1, 2, 10, 0)))
        # 强制收盘在高位以便若开启 TL 也能过；此处 TL 已关
        bar = make_bar(92, 98, 91, 97, dt=datetime(2024, 1, 2, 10, 30))
        first = match_opp04(s, bar, "STRONG_BULL", atr_5=10.0, tick=1.0, stop_buffer=1.0)
        self.assertTrue(first, "expected OPP04 long match")
        self.assertTrue(first[0].setup.endswith("_LONG"))
        note_opp04_consumed(s, first[0].setup)
        second = match_opp04(s, bar, "STRONG_BULL", atr_5=10.0, tick=1.0, stop_buffer=1.0)
        self.assertEqual(second, [])

    def test_tl_breakout_tick_boundary(self) -> None:
        from strategies.pa_minimal.detectors.opp04 import _segment_peak_point

        bars = _ll3_fixture_bars()
        pk1 = _segment_peak_point(bars, 4, 10)
        pk2 = _segment_peak_point(bars, 10, 16)
        assert pk1 is not None and pk2 is not None
        tl = _tl_price_at(pk1[0], pk1[1], pk2[0], pk2[1], len(bars) - 1)
        # close == tl 不破；close == tl + tick 仍不破（需严格 >）；再大一跳才破
        self.assertFalse(
            _pullback_tl_breakout_long(bars, 4, 10, 16, close=tl, tick=1.0)
        )
        self.assertFalse(
            _pullback_tl_breakout_long(bars, 4, 10, 16, close=tl + 1.0, tick=1.0)
        )
        self.assertTrue(
            _pullback_tl_breakout_long(bars, 4, 10, 16, close=tl + 1.01, tick=1.0)
        )


if __name__ == "__main__":
    unittest.main()
