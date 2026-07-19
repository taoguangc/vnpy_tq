"""PAAF vn.py adapter 单测（无 Parquet）。"""

from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

from strategies.paaf.adapters import (
    PaafBar,
    am_is_inited,
    bar_from_vnpy,
    bars_from_am,
    last_bar,
)


class _FakeAM:
    def __init__(
        self,
        *,
        opens: list[float],
        highs: list[float],
        lows: list[float],
        closes: list[float],
        volumes: list[float] | None = None,
        inited: bool = True,
    ) -> None:
        self.open = opens
        self.high = highs
        self.low = lows
        self.close = closes
        self.volume = volumes if volumes is not None else [0.0] * len(closes)
        self.count = len(closes)
        self.inited = inited


class TestVnpyAdapter(unittest.TestCase):
    def test_bar_from_vnpy(self) -> None:
        bar = BarData(
            gateway_name="TEST",
            symbol="rb2501",
            exchange=Exchange.SHFE,
            datetime=datetime(2026, 7, 19, 9, 1),
            interval=Interval.MINUTE,
            volume=10.0,
            turnover=0.0,
            open_interest=100.0,
            open_price=3500.0,
            high_price=3510.0,
            low_price=3490.0,
            close_price=3505.0,
        )
        paaf = bar_from_vnpy(bar)
        self.assertIsInstance(paaf, PaafBar)
        self.assertEqual(paaf.open, 3500.0)
        self.assertEqual(paaf.high, 3510.0)
        self.assertEqual(paaf.low, 3490.0)
        self.assertEqual(paaf.close, 3505.0)
        self.assertEqual(paaf.volume, 10.0)
        self.assertEqual(paaf.open_interest, 100.0)
        self.assertEqual(paaf.symbol, "rb2501")
        self.assertEqual(paaf.datetime, datetime(2026, 7, 19, 9, 1))

    def test_bars_from_am_and_last_bar(self) -> None:
        am = _FakeAM(
            opens=[1.0, 2.0, 3.0],
            highs=[1.5, 2.5, 3.5],
            lows=[0.5, 1.5, 2.5],
            closes=[1.2, 2.2, 3.2],
            volumes=[10.0, 20.0, 30.0],
        )
        self.assertTrue(am_is_inited(am))
        bars = bars_from_am(am, lookback=2)
        self.assertEqual(len(bars), 2)
        self.assertEqual(bars[0].close, 2.2)
        self.assertEqual(bars[1].close, 3.2)
        self.assertIsNone(bars[1].datetime)

        tip = last_bar(am)
        assert tip is not None
        self.assertEqual(tip.close, 3.2)
        self.assertEqual(tip.open, 3.0)

    def test_uninited_am_returns_empty(self) -> None:
        am = _FakeAM(
            opens=[],
            highs=[],
            lows=[],
            closes=[],
            inited=False,
        )
        self.assertFalse(am_is_inited(am))
        self.assertEqual(bars_from_am(am), [])
        self.assertIsNone(last_bar(am))

    def test_domain_has_no_vnpy_import(self) -> None:
        domain_path = (
            Path(__file__).resolve().parents[1]
            / "strategies"
            / "paaf"
            / "domain.py"
        )
        text = domain_path.read_text(encoding="utf-8")
        self.assertNotIn("vnpy", text)


if __name__ == "__main__":
    unittest.main()
