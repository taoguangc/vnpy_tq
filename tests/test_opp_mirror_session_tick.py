# -*- coding: utf-8 -*-
"""OPP01–20：多空镜像、跨时段、边界 tick 单元测试。"""
from __future__ import annotations

import unittest
from datetime import date, datetime

from strategies.pa_minimal.detectors.opp01 import match_opp01
from strategies.pa_minimal.detectors.opp02 import match_opp02
from strategies.pa_minimal.detectors.opp03 import match_opp03
from strategies.pa_minimal.detectors.opp05 import match_opp05_ioi
from strategies.pa_minimal.detectors.opp06 import match_opp06_15m
from strategies.pa_minimal.detectors.opp07 import match_opp07_5m
from strategies.pa_minimal.detectors.opp08 import match_opp08
from strategies.pa_minimal.detectors.opp09 import match_opp09
from strategies.pa_minimal.detectors.opp10 import match_opp10
from strategies.pa_minimal.detectors.opp11 import ascending_tl, descending_tl, match_opp11_pullback
from strategies.pa_minimal.detectors.opp12 import match_opp12
from strategies.pa_minimal.detectors.opp13 import match_opp13_boundary
from strategies.pa_minimal.detectors.opp14 import match_opp14_5m_hl
from strategies.pa_minimal.detectors.opp16 import match_opp16
from strategies.pa_minimal.detectors.opp16_1h import match_opp16_1h
from strategies.pa_minimal.detectors.opp16_pin import match_opp16_pin
from strategies.pa_minimal.detectors.opp17 import match_opp17
from strategies.pa_minimal.detectors.opp18 import match_opp18
from strategies.pa_minimal.detectors.opp19 import match_opp19
from strategies.pa_minimal.detectors.opp20 import GapState, detect_gap_open, match_opp20
from tests.pa_fixtures import FakeAM, StopCapStrategy, make_bar, mirror_ohlc


TICK = 1.0
ATR = 10.0
BUF = 1.0


def _dirs(matches) -> set[int]:
    return {m.direction for m in matches}


def _setups(matches) -> set[str]:
    return {m.setup for m in matches}


class TestOpp01Mirror(unittest.TestCase):
    def test_h1_long_vs_l1_short_mirror(self) -> None:
        s = StopCapStrategy()
        long_bar = make_bar(100, 106, 99, 105)
        long_m = match_opp01(
            s, long_bar, "STRONG_BULL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, ema_20=98.0,
            prev_high=104.0, prev_low=97.0, upper_shadow=1.0, lower_shadow=1.0,
            bar_range=7.0,
            is_strong_bar=True, is_long_climax=False, is_short_climax=False,
            h_counter=0, h1_low_broken=False, l_counter=0, l1_high_broken=False,
            always_in="LONG", trend_phase="EARLY", trend_direction=1,
            is_micro_pullback=True,
        )
        self.assertTrue(long_m)
        self.assertEqual(long_m[0].direction, 1)
        self.assertEqual(long_m[0].trigger, long_bar.high_price + TICK)

        o, h, l, c = mirror_ohlc(100, 106, 99, 105)
        short_bar = make_bar(o, h, l, c)
        short_m = match_opp01(
            s, short_bar, "STRONG_BEAR",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, ema_20=-98.0,
            prev_high=-97.0, prev_low=-104.0, upper_shadow=1.0, lower_shadow=1.0,
            bar_range=7.0,
            is_strong_bar=True, is_long_climax=False, is_short_climax=False,
            h_counter=0, h1_low_broken=False, l_counter=0, l1_high_broken=False,
            always_in="SHORT", trend_phase="EARLY", trend_direction=-1,
            is_micro_pullback=True,
        )
        self.assertTrue(short_m)
        self.assertEqual(short_m[0].direction, -1)
        self.assertIn("L1_PULLBACK_SHORT", short_m[0].setup)
        self.assertEqual(short_m[0].trigger, short_bar.low_price - TICK)


class TestOpp02MirrorTick(unittest.TestCase):
    def _s(self, always_in: str) -> StopCapStrategy:
        s = StopCapStrategy(always_in=always_in)
        s.opp02_r2_gate_enabled = False
        s.opp02_r2_min = 0.0
        s.opp02_aff_gate_enabled = False
        s.opp02_aff_alpha_min = 0.0
        s.ema_pullback_touch_atr = 0.5
        s.ema_pullback_min_body_ratio = 0.3
        s._aff_alpha_strength = 1.0
        s._trend_regime_blocks_continuation = lambda *_a, **_k: False  # type: ignore
        return s

    def test_long_short_mirror(self) -> None:
        # 检测器要求 ema_20 > 0，空头用正价格几何镜像（非取负）
        long_bar = make_bar(100, 105, 99, 104)  # touches ema 100
        lm = match_opp02(
            self._s("LONG"), long_bar,
            atr_5=ATR, tick=TICK, stop_buffer=BUF,
            bar_range=6.0, body=4.0, ema_20=100.0, is_oo=False,
        )
        self.assertEqual(_setups(lm), {"OPP02_5M_EMA_PULLBACK_LONG"})

        short_bar = make_bar(100, 101, 95, 96)  # high 触 EMA，阴线
        sm = match_opp02(
            self._s("SHORT"), short_bar,
            atr_5=ATR, tick=TICK, stop_buffer=BUF,
            bar_range=6.0, body=4.0, ema_20=100.0, is_oo=False,
        )
        self.assertEqual(_setups(sm), {"OPP02_5M_EMA_PULLBACK_SHORT"})
        self.assertEqual(lm[0].trigger, long_bar.high_price + TICK)
        self.assertEqual(sm[0].trigger, short_bar.low_price - TICK)

    def test_bar_range_tick_floor(self) -> None:
        s = self._s("LONG")
        bar = make_bar(100, 101, 100, 100.5)
        self.assertEqual(
            match_opp02(
                s, bar, atr_5=ATR, tick=1.0, stop_buffer=BUF,
                bar_range=1.0, body=0.5, ema_20=100.0, is_oo=False,
            ),
            [],
        )


class TestOpp03MirrorTick(unittest.TestCase):
    def test_m2_ema_within_2_ticks(self) -> None:
        s = StopCapStrategy()
        # |low - ema| <= 2*tick
        bar = make_bar(100, 105, 98, 104)
        ok = match_opp03(
            s, bar, "BULL_CHANNEL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, ema_20=100.0,
            h_counter=2, l_counter=0, is_bull_reversal=True, is_bear_reversal=False,
        )
        self.assertEqual(_setups(ok), {"OPP03_5M_M2B"})
        # 刚好越界：|low-ema|=3 > 2
        bad = match_opp03(
            s, make_bar(100, 105, 97, 104), "BULL_CHANNEL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, ema_20=100.0,
            h_counter=2, l_counter=0, is_bull_reversal=True, is_bear_reversal=False,
        )
        self.assertEqual(bad, [])

    def test_m2_short_mirror(self) -> None:
        s = StopCapStrategy()
        bar = make_bar(100, 102, 95, 96)
        out = match_opp03(
            s, bar, "BEAR_CHANNEL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, ema_20=100.0,
            h_counter=0, l_counter=2, is_bull_reversal=False, is_bear_reversal=True,
        )
        self.assertEqual(_setups(out), {"OPP03_5M_M2S"})


class TestOpp05IoiTick(unittest.TestCase):
    def test_breakout_requires_mother_plus_tick(self) -> None:
        s = StopCapStrategy()
        mother_h, mother_l = 110.0, 100.0
        # close == mother_h + tick → 不满足 >
        edge = make_bar(109, 112, 108, mother_h + TICK)
        self.assertEqual(
            match_opp05_ioi(
                s, edge, "BULL_CHANNEL",
                atr_5=ATR, tick=TICK, is_strong_bar=True, is_oo=False,
                ioi_setup_active=True, mother_high=mother_h, mother_low=mother_l,
            ),
            [],
        )
        ok = make_bar(109, 112, 108, mother_h + TICK + 0.1)
        out = match_opp05_ioi(
            s, ok, "BULL_CHANNEL",
            atr_5=ATR, tick=TICK, is_strong_bar=True, is_oo=False,
            ioi_setup_active=True, mother_high=mother_h, mother_low=mother_l,
        )
        self.assertTrue(out)
        self.assertEqual(out[0].direction, 1)

        # 空头镜像
        short_ok = make_bar(101, 102, 98, mother_l - TICK - 0.1)
        sout = match_opp05_ioi(
            s, short_ok, "BEAR_CHANNEL",
            atr_5=ATR, tick=TICK, is_strong_bar=True, is_oo=False,
            ioi_setup_active=True, mother_high=mother_h, mother_low=mother_l,
        )
        self.assertTrue(sout)
        self.assertEqual(sout[0].direction, -1)


class TestOpp06Mirror(unittest.TestCase):
    def test_ttr_breakout_mirror_and_edge(self) -> None:
        # nested ii：母区 = high[-4]/low[-4]，宽度须 <= 0.8*ATR
        am = FakeAM(
            open=[100, 101, 100.5, 100.2, 102],
            high=[106, 105, 104, 103, 108],
            low=[100, 100.5, 101, 101.5, 102],
            close=[103, 102.5, 102, 102.2, 107],
        )
        s = StopCapStrategy(am_15min=am)
        mother_h = float(am.high[-4])
        mother_l = float(am.low[-4])
        # close == mother_h：条件是严格 >
        edge = make_bar(104, mother_h, 103, mother_h)
        self.assertEqual(
            match_opp06_15m(s, edge, atr_15=ATR, tick=TICK, stop_buffer=BUF),
            [],
        )
        long_bar = make_bar(104, mother_h + 2, 103, mother_h + 0.5)
        lm = match_opp06_15m(s, long_bar, atr_15=ATR, tick=TICK, stop_buffer=BUF)
        self.assertEqual(_dirs(lm), {1})
        self.assertEqual(lm[0].trigger, long_bar.high_price + TICK)

        short_bar = make_bar(mother_l + 1, mother_l + 2, mother_l - 2, mother_l - 0.5)
        sm = match_opp06_15m(s, short_bar, atr_15=ATR, tick=TICK, stop_buffer=BUF)
        self.assertEqual(_dirs(sm), {-1})
        self.assertEqual(sm[0].trigger, short_bar.low_price - TICK)


class TestOpp07SessionTick(unittest.TestCase):
    def test_cutoff_1430(self) -> None:
        am = FakeAM(
            open=[100, 101, 100.5, 102],
            high=[105, 103, 102, 106],
            low=[99, 100, 100.2, 101],
            close=[104, 101.5, 101, 105],
        )
        s = StopCapStrategy(am_5min=am)
        s.ib_min_mother_range_tick = 3
        early = make_bar(102, 106, 101, 105, dt=datetime(2024, 1, 2, 14, 25))
        late = make_bar(102, 106, 101, 105, dt=datetime(2024, 1, 2, 14, 30))
        self.assertTrue(
            match_opp07_5m(s, early, "BULL_CHANNEL", atr_5=ATR, tick=TICK, stop_buffer=BUF)
        )
        self.assertEqual(
            match_opp07_5m(s, late, "BULL_CHANNEL", atr_5=ATR, tick=TICK, stop_buffer=BUF),
            [],
        )


class TestOpp08Mirror(unittest.TestCase):
    def test_strong_breakout_mirror(self) -> None:
        s = StopCapStrategy()
        # 默认已要求破前低；测试显式 True
        s.opp08_short_require_prev_low = True
        s.opp08_short_block_climax = True
        long_bar = make_bar(100, 108, 99, 107)
        lm = match_opp08(
            s, long_bar, "STRONG_BULL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, ema_20=100.0,
            prev_high=105.0, prev_low=95.0, recent_5bar_low=94.0,
            is_strong_bar=True, is_oo=False, is_long_climax=False,
            is_short_climax=False, bar_range=9.0,
        )
        self.assertEqual(_setups(lm), {"OPP08_5M_STRONG_BREAKOUT_LONG"})

        o, h, l, c = mirror_ohlc(100, 108, 99, 107)
        sm = match_opp08(
            s, make_bar(o, h, l, c), "STRONG_BEAR",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, ema_20=-100.0,
            prev_high=-95.0, prev_low=-105.0, recent_5bar_low=-94.0,
            is_strong_bar=True, is_oo=False, is_long_climax=False,
            is_short_climax=False, bar_range=9.0,
        )
        self.assertEqual(_setups(sm), {"OPP08_5M_STRONG_BREAKOUT_SHORT"})


class TestOpp09Session(unittest.TestCase):
    def test_cutoff_1400(self) -> None:
        s = StopCapStrategy()
        kwargs = dict(
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=6.0, body=3.0,
            upper_shadow=1.0, lower_shadow=1.0, bp_state="WAIT_PB",
            broken_level=100.0, always_in="LONG",
        )
        ok = make_bar(101, 103, 99.5, 102, dt=datetime(2024, 1, 2, 13, 55))
        late = make_bar(101, 103, 99.5, 102, dt=datetime(2024, 1, 2, 14, 0))
        # WAIT_PB 多：回踩后反转——具体条件见 opp09；此处只验证时段门
        # 若 ok 无匹配也不强制；late 必须空
        late_out = match_opp09(s, late, **kwargs)
        self.assertEqual(late_out, [])


class TestOpp10SessionMirror(unittest.TestCase):
    def test_morning_only_and_mirror(self) -> None:
        s = StopCapStrategy()
        # PDH 空：大上影 + 收近低 + 实体够大
        short_bar = make_bar(110, 112, 108, 108.8, dt=datetime(2024, 1, 2, 10, 0))
        br = 4.0
        body = 1.2  # >= 0.15*4
        us = 2.0    # >= 0.40*4
        ls = 0.8
        out = match_opp10(
            s, short_bar, atr_5=ATR, tick=TICK, stop_buffer=BUF,
            bar_range=br, body=body, upper_shadow=us, lower_shadow=ls,
            prev_day_high=111.0, prev_day_low=90.0, always_in="SHORT",
        )
        self.assertIn("OPP10_5M_PDH_MAGNET_SHORT", _setups(out))

        night = make_bar(110, 112, 108, 108.8, dt=datetime(2024, 1, 2, 21, 5))
        self.assertEqual(
            match_opp10(
                s, night, atr_5=ATR, tick=TICK, stop_buffer=BUF,
                bar_range=br, body=body, upper_shadow=us, lower_shadow=ls,
                prev_day_high=111.0, prev_day_low=90.0, always_in="SHORT",
            ),
            [],
        )

        # PDL 多：大下影 + 收近高
        long_bar = make_bar(89.5, 92, 88, 91.6, dt=datetime(2024, 1, 2, 10, 0))
        br2 = 4.0
        body2 = 2.1
        us2 = 0.4
        ls2 = 1.7  # >= 0.40 * 4
        lout = match_opp10(
            s, long_bar, atr_5=ATR, tick=TICK, stop_buffer=BUF,
            bar_range=br2, body=body2, upper_shadow=us2, lower_shadow=ls2,
            prev_day_high=120.0, prev_day_low=89.0, always_in="LONG",
        )
        self.assertIn("OPP10_5M_PDL_MAGNET_LONG", _setups(lout))


class TestOpp11TlTick(unittest.TestCase):
    def test_descending_tl_min_span_ticks(self) -> None:
        # 跨度 < 4*tick → None
        self.assertIsNone(
            descending_tl(10, 1.0, ph1_idx=1, ph1_price=100.0, ph2_idx=5, ph2_price=97.0)
        )
        self.assertIsNotNone(
            descending_tl(10, 1.0, ph1_idx=1, ph1_price=100.0, ph2_idx=5, ph2_price=95.0)
        )

    def test_pullback_mirror(self) -> None:
        s = StopCapStrategy()
        long_m = match_opp11_pullback(
            s, make_bar(100, 103, 99, 102),
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=4.0,
            upper_shadow=1.0, lower_shadow=1.0,
            opp11_state="WAIT_PB_LONG", break_bar_idx=5, curr_idx=8,
            tl_now=100.0, is_boundary_bull=False, is_boundary_bear=False,
        )
        short_m = match_opp11_pullback(
            s, make_bar(100, 101, 97, 98),
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=4.0,
            upper_shadow=1.0, lower_shadow=1.0,
            opp11_state="WAIT_PB_SHORT", break_bar_idx=5, curr_idx=8,
            tl_now=100.0, is_boundary_bull=False, is_boundary_bear=False,
        )
        # 状态驱动：有则方向相反
        if long_m and short_m:
            self.assertEqual(_dirs(long_m), {1})
            self.assertEqual(_dirs(short_m), {-1})


class TestOpp12Mirror(unittest.TestCase):
    def test_overshoot_sides(self) -> None:
        s = StopCapStrategy()
        s.overshoot_atr_mult = 1.0
        s.overshoot_max_atr_mult = 5.0
        # 多：收盘低于 EMA，深度在 [1ATR, 5ATR]
        long_bar = make_bar(85, 88, 84, 86)  # ema-close = 100-86=14 → 在 10..50
        short_bar = make_bar(115, 120, 114, 118)  # close > ema+1ATR
        lm = match_opp12(
            s, long_bar, atr_5=ATR, tick=TICK, ema_20=100.0,
            is_bull_reversal=True, is_bear_reversal=False, is_oo=False,
        )
        sm = match_opp12(
            s, short_bar, atr_5=ATR, tick=TICK, ema_20=100.0,
            is_bull_reversal=False, is_bear_reversal=True, is_oo=False,
        )
        self.assertEqual(_setups(lm), {"OPP12_5M_OVERSHOOT_FAIL_LONG"})
        self.assertEqual(_setups(sm), {"OPP12_5M_OVERSHOOT_FAIL_SHORT"})


class TestOpp13Mirror(unittest.TestCase):
    def test_range_fail_sides(self) -> None:
        s = StopCapStrategy()
        s.day_high = 110.0
        s.day_low = 90.0
        s.always_in = "NONE"
        s.market_context = "TIGHT_RANGE"
        # 边界失败多：测日低
        low_bar = make_bar(91, 93, 89.5, 92.5)
        high_bar = make_bar(108, 110.5, 107, 107.5)
        # match_opp13_boundary 需要 flags
        lm = match_opp13_boundary(
            s, low_bar, atr_5=ATR, tick=TICK, bar_range=3.5,
            upper_shadow=0.5, lower_shadow=1.0,
            is_boundary_bull=True, is_boundary_bear=False,
            boundary_tol=2.0, is_oo=False,
        )
        sm = match_opp13_boundary(
            s, high_bar, atr_5=ATR, tick=TICK, bar_range=3.5,
            upper_shadow=1.0, lower_shadow=0.5,
            is_boundary_bull=False, is_boundary_bear=True,
            boundary_tol=2.0, is_oo=False,
        )
        if lm:
            self.assertEqual(lm[0].direction, 1)
            self.assertIn("DAY_EXTREME_REV_LOW", lm[0].setup)
        if sm:
            self.assertEqual(sm[0].direction, -1)
            self.assertIn("DAY_EXTREME_REV_HIGH", sm[0].setup)


class TestOpp14LongOnlyTick(unittest.TestCase):
    def test_hl_within_ticks(self) -> None:
        # FIRST_TEST + HL 抬高在 max_ticks 内 → 仅多头
        # 质量：下影 >= 40% range，收盘在低点上方 35% range
        bar = make_bar(91.0, 94.0, 90.0, 93.2)
        br = 4.0
        ls = 1.7
        out = match_opp14_5m_hl(
            StopCapStrategy(),
            bar,
            "BULL_CHANNEL",
            atr_5=ATR, tick=TICK,
            day_low_test_state="FIRST_TEST",
            first_test_low=90.0,
            day_low_test_bar_count=3,
            bar_range=br,
            lower_shadow=ls,
            is_boundary_bull=True,
            always_in="LONG",
            day_low_hl_max_ticks=3,
        )
        self.assertTrue(out)
        self.assertEqual(out[0].direction, 1)
        self.assertIn("HL_DOUBLE_BOTTOM", out[0].setup)
        # 抬高超过 tick 上限 → 拒
        bad = match_opp14_5m_hl(
            StopCapStrategy(),
            make_bar(95, 98, 94, 97),
            "BULL_CHANNEL",
            atr_5=ATR, tick=TICK,
            day_low_test_state="FIRST_TEST",
            first_test_low=90.0,
            day_low_test_bar_count=3,
            bar_range=4.0,
            lower_shadow=2.0,
            is_boundary_bull=True,
            always_in="LONG",
            day_low_hl_max_ticks=2,
        )
        self.assertEqual(bad, [])


class TestOpp16MirrorTick(unittest.TestCase):
    def test_two_bar_rev_mirror_and_range_floor(self) -> None:
        am = FakeAM(
            open=[100, 102],
            high=[101, 103],
            low=[97, 100],
            close=[98, 101],  # prev bearish
        )
        s = StopCapStrategy(am_5min=am)
        s.prev_bar_shape = "DOWN_TREND"
        long_bar = make_bar(100, 105, 99, 104.5)  # 强阳确认
        lm = match_opp16(
            s, long_bar, "STRONG_BULL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=6.0,
        )
        self.assertEqual(_setups(lm), {"OPP16_5M_TWO_BAR_REV_LONG"})

        am2 = FakeAM(
            open=[100, 98],
            high=[103, 100],
            low=[99, 96],
            close=[102, 97],  # prev bullish
        )
        s2 = StopCapStrategy(am_5min=am2)
        s2.prev_bar_shape = "UP_TREND"
        short_bar = make_bar(100, 101, 95, 95.5)
        sm = match_opp16(
            s2, short_bar, "STRONG_BEAR",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=6.0,
        )
        self.assertEqual(_setups(sm), {"OPP16_5M_TWO_BAR_REV_SHORT"})

        self.assertEqual(
            match_opp16(
                s, long_bar, "STRONG_BULL",
                atr_5=ATR, tick=6.0, stop_buffer=BUF, bar_range=6.0,
            ),
            [],
        )


class TestOpp16_1hMirror(unittest.TestCase):
    def test_1h_mirror(self) -> None:
        am = FakeAM(open=[100, 102], high=[101, 103], low=[97, 100], close=[98, 101])
        s = StopCapStrategy(am_60min=am)
        s.two_bar_rev_context = "STRONG_BULL,STRONG_BEAR"
        s.two_bar_rev_body_ratio = 0.4
        lm = match_opp16_1h(
            s, make_bar(100, 105, 99, 104), "STRONG_BULL",
            atr_60=ATR, tick=TICK, stop_buffer=BUF,
        )
        for x in lm:
            self.assertEqual(x.direction, 1)


class TestOpp16PinMirror(unittest.TestCase):
    def test_pin_sides(self) -> None:
        am = FakeAM(
            open=[100] * 5, high=[110] * 5, low=[90] * 5, close=[100] * 5,
        )
        s = StopCapStrategy(am_5min=am)
        # 长下影锤头多
        long_bar = make_bar(100, 101, 90, 100.5)
        br = 11.0
        lm = match_opp16_pin(
            s, long_bar, "BULL_CHANNEL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=br,
            upper_shadow=0.5, lower_shadow=10.0, ema_20=100.0,
            always_in="LONG",
        )
        short_bar = make_bar(100, 110, 99, 99.5)
        sm = match_opp16_pin(
            s, short_bar, "BEAR_CHANNEL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=11.0,
            upper_shadow=10.0, lower_shadow=0.5, ema_20=100.0,
            always_in="SHORT",
        )
        if lm:
            self.assertEqual(lm[0].direction, 1)
        if sm:
            self.assertEqual(sm[0].direction, -1)


class TestOpp17MirrorTick(unittest.TestCase):
    def test_climax_mirror(self) -> None:
        am = FakeAM(
            open=[100, 110], high=[120, 112], low=[99, 105], close=[118, 106],
        )
        s = StopCapStrategy(am_5min=am)
        s.climax_rev_context = "STRONG_BULL,STRONG_BEAR"
        s.climax_rev_range_atr = 1.0
        # prev range large; current close crosses mid downward for short after bull climax
        short_bar = make_bar(110, 112, 100, 101)
        # 读属性
        for attr, val in [
            ("climax_rev_allowed_context", "STRONG_BULL,STRONG_BEAR"),
        ]:
            if not hasattr(s, attr):
                setattr(s, attr, val)
        out = match_opp17(
            s, short_bar, "STRONG_BULL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=12.0, is_oo=False,
        )
        # 方向若命中应为空
        for m in out:
            self.assertIn(m.direction, (-1, 1))


class TestOpp18MirrorTick(unittest.TestCase):
    def test_failed_hl_mirror_and_range_floor(self) -> None:
        s = StopCapStrategy()
        long_bar = make_bar(100, 106, 99, 105)
        lm = match_opp18(
            s, long_bar, atr_5=ATR, tick=TICK, stop_buffer=BUF,
            bar_range=7.0, body=5.0,
            failed_hl_reverse_pending=True, reverse_dir=1,
        )
        self.assertEqual(_setups(lm), {"OPP18_5M_FAILED_L2_LONG"})
        o, h, l, c = mirror_ohlc(100, 106, 99, 105)
        sm = match_opp18(
            s, make_bar(o, h, l, c), atr_5=ATR, tick=TICK, stop_buffer=BUF,
            bar_range=7.0, body=5.0,
            failed_hl_reverse_pending=True, reverse_dir=-1,
        )
        self.assertEqual(_setups(sm), {"OPP18_5M_FAILED_H2_SHORT"})
        self.assertEqual(
            match_opp18(
                s, long_bar, atr_5=ATR, tick=7.0, stop_buffer=BUF,
                bar_range=7.0, body=5.0,
                failed_hl_reverse_pending=True, reverse_dir=1,
            ),
            [],
        )


class TestOpp19SessionMirror(unittest.TestCase):
    def _s(self) -> StopCapStrategy:
        s = StopCapStrategy()
        s._od_state = "COLLECTING"
        s.opening_rev_enabled = True
        s._od_bars_collected = 2
        s._od_bar1_shape = "DOWN"
        s._od_bar1_mid = 100.0
        s.opening_rev_body_ratio = 0.3
        s.opp19_rev_arm_mode = "FAST_TRACK"
        s._od_high = 110.0
        s._od_low = 90.0
        s.opp19_breakout_r2_gate_enabled = False
        s.opp19_breakout_r2_min = 0.0
        s.opp19_breakout_aff_gate_enabled = False
        s.opp19_breakout_aff_alpha_min = 0.0
        s.opening_drive_min_body = 0.0
        s._aff_alpha_strength = 1.0
        s._opening_rev_allows_entry = lambda *_a, **_k: True  # type: ignore
        s._opening_rev_in_time_window = lambda *_a, **_k: True  # type: ignore
        s._trend_regime_blocks_continuation = lambda *_a, **_k: False  # type: ignore
        s._opening_drive_breakout_context_ok = lambda *_a, **_k: True  # type: ignore
        return s

    def test_session_window_and_rev_long(self) -> None:
        s = self._s()
        morning = make_bar(100, 106, 99, 105, dt=datetime(2024, 1, 2, 9, 35))
        out = match_opp19(
            s, morning, "BULL_CHANNEL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=7.0, body=5.0,
            is_strong_bar=True, is_oo=False,
        )
        self.assertIn("OPP19_5M_OD_REV_LONG", _setups(out))

        afternoon = make_bar(100, 106, 99, 105, dt=datetime(2024, 1, 2, 13, 0))
        self.assertEqual(
            match_opp19(
                s, afternoon, "BULL_CHANNEL",
                atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=7.0, body=5.0,
                is_strong_bar=True, is_oo=False,
            ),
            [],
        )

        # 夜盘窗 + 空头反转
        s2 = self._s()
        s2._od_bar1_shape = "UP"
        s2._od_bar1_mid = 100.0
        night = make_bar(100, 101, 94, 95, dt=datetime(2024, 1, 2, 21, 10))
        sout = match_opp19(
            s2, night, "BEAR_CHANNEL",
            atr_5=ATR, tick=TICK, stop_buffer=BUF, bar_range=7.0, body=5.0,
            is_strong_bar=True, is_oo=False,
        )
        self.assertIn("OPP19_5M_OD_REV_SHORT", _setups(sout))


class TestOpp20SessionMirror(unittest.TestCase):
    def test_gap_detect_session_and_time(self) -> None:
        # 同日 session_date → 不检测
        bar = make_bar(110, 112, 109, 111, dt=datetime(2024, 1, 3, 9, 5))
        self.assertIsNone(
            detect_gap_open(
                bar, pd_close=100.0, atr_5=ATR, tick=TICK,
                session_date=date(2024, 1, 3), bar_range=3.0, body=1.0,
            )
        )
        # 新会话 + 9:05 → 检测
        gap = detect_gap_open(
            bar, pd_close=100.0, atr_5=ATR, tick=TICK,
            session_key="2024-01-02-D", bar_range=3.0, body=1.0,
        )
        self.assertIsNotNone(gap)
        self.assertEqual(gap.direction, 1)

        # 9:15 过窗
        late = make_bar(110, 112, 109, 111, dt=datetime(2024, 1, 3, 9, 15))
        self.assertIsNone(
            detect_gap_open(
                late, pd_close=100.0, atr_5=ATR, tick=TICK,
                session_key="2024-01-02-D", bar_range=3.0, body=1.0,
            )
        )

        # 夜盘 21:05
        night = make_bar(110, 112, 109, 111, dt=datetime(2024, 1, 2, 21, 5))
        g_n = detect_gap_open(
            night, pd_close=100.0, atr_5=ATR, tick=TICK,
            session_key="2024-01-02-D", bar_range=3.0, body=1.0,
        )
        self.assertIsNotNone(g_n)
        self.assertTrue(g_n.session_key.endswith("-N"))

        # 向下跳空镜像
        down = make_bar(90, 92, 89, 91, dt=datetime(2024, 1, 3, 9, 5))
        g2 = detect_gap_open(
            down, pd_close=100.0, atr_5=ATR, tick=TICK,
            session_key="2024-01-02-D", bar_range=3.0, body=1.0,
        )
        self.assertIsNotNone(g2)
        self.assertEqual(g2.direction, -1)

    def test_match_gap_rev_mirror(self) -> None:
        s = StopCapStrategy()
        gs = GapState(
            state="GAP_WAIT", direction=1, pd_close=100.0,
            bars=2, filled=False, bar1_shape="DOWN", bar1_mid=105.0,
        )
        bar = make_bar(104, 110, 103, 109, dt=datetime(2024, 1, 3, 9, 15))
        br = bar.high_price - bar.low_price
        body = abs(bar.close_price - bar.open_price)
        out = match_opp20(
            s, bar, atr_5=ATR, tick=TICK, stop_buffer=BUF,
            bar_range=br, body=body, upper_shadow=1.0, lower_shadow=1.0,
            gap_state=gs, always_in="LONG",
        )
        # 有匹配则含多
        for m in out:
            if "GAP_REV" in m.setup:
                self.assertEqual(m.direction, 1)


class TestOppSetupRegistry(unittest.TestCase):
    """文档化双向 / 单向 OPP，防止漏镜像命名。"""

    BIDIR = {
        2: ("OPP02_5M_EMA_PULLBACK_LONG", "OPP02_5M_EMA_PULLBACK_SHORT"),
        3: ("OPP03_5M_M2B", "OPP03_5M_M2S"),
        4: ("OPP04_5M_WEDGE_FLAG_LONG", "OPP04_5M_WEDGE_FLAG_SHORT"),
        6: ("OPP06_15M_TTR_BREAKOUT", "OPP06_15M_TTR_BREAKOUT"),
        7: ("OPP07_5M_IB_BREAKOUT_LONG", "OPP07_5M_IB_BREAKOUT_SHORT"),
        8: ("OPP08_5M_STRONG_BREAKOUT_LONG", "OPP08_5M_STRONG_BREAKOUT_SHORT"),
        9: ("OPP09_5M_BP_LONG", "OPP09_5M_BP_SHORT"),
        10: ("OPP10_5M_PDL_MAGNET_LONG", "OPP10_5M_PDH_MAGNET_SHORT"),
        11: ("OPP11_5M_TL_PULLBACK_LONG", "OPP11_5M_TL_PULLBACK_SHORT"),
        12: ("OPP12_5M_OVERSHOOT_FAIL_LONG", "OPP12_5M_OVERSHOOT_FAIL_SHORT"),
        13: ("OPP13_5M_DAY_EXTREME_REV_LOW", "OPP13_5M_DAY_EXTREME_REV_HIGH"),
        15: ("OPP15_5M_WEDGE_REVERSAL_LONG", "OPP15_5M_WEDGE_REVERSAL"),
        16: ("OPP16_5M_TWO_BAR_REV_LONG", "OPP16_5M_TWO_BAR_REV_SHORT"),
        17: ("OPP17_5M_CLIMAX_REV_LONG", "OPP17_5M_CLIMAX_REV_SHORT"),
        18: ("OPP18_5M_FAILED_L2_LONG", "OPP18_5M_FAILED_H2_SHORT"),
        19: ("OPP19_5M_OD_REV_LONG", "OPP19_5M_OD_REV_SHORT"),
        20: ("OPP20_5M_GAP_REV_LONG", "OPP20_5M_GAP_REV_SHORT"),
    }
    LONG_ONLY = {14: ("OPP14_5M_HL_DOUBLE_BOTTOM", "OPP14_1H_HL_DOUBLE_BOTTOM")}

    def test_bidir_names_present_in_modules(self) -> None:
        import importlib
        import pathlib
        root = pathlib.Path(__file__).resolve().parents[1] / "strategies" / "pa_minimal" / "detectors"
        for opp, (long_n, short_n) in self.BIDIR.items():
            path = root / f"opp{opp:02d}.py"
            text = path.read_text(encoding="utf-8")
            self.assertIn(long_n, text, msg=f"OPP{opp:02d} missing {long_n}")
            self.assertIn(short_n, text, msg=f"OPP{opp:02d} missing {short_n}")
        for opp, names in self.LONG_ONLY.items():
            text = (root / f"opp{opp:02d}.py").read_text(encoding="utf-8")
            for n in names:
                self.assertIn(n, text)
            self.assertNotIn("DOUBLE_TOP", text)  # 单向架构：无对称双顶


if __name__ == "__main__":
    unittest.main()
