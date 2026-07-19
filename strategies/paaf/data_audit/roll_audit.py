"""Method A (CbC unadjusted) roll-neighborhood audit — pure metrics, no trading."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class RollGapRecord:
    """One contract roll gap on an unadjusted continuous series."""

    roll_index: int
    timestamp: datetime
    from_yymm: str
    to_yymm: str
    prev_close: float
    next_open: float
    gap_abs: float
    gap_rel: float


@dataclass(frozen=True)
class RollAuditSummary:
    """Primary + secondary roll audit aggregates for Method A."""

    roll_count: int
    gap_abs_mean: float
    gap_abs_median: float
    gap_rel_mean: float
    gap_rel_median: float
    neighborhood_vol: float
    non_roll_vol: float
    vol_ratio: float
    neighborhood_abs_return_p95: float
    non_roll_abs_return_p95: float
    abs_return_p95_ratio: float
    atr_ratio_neighborhood_mean: float | None
    atr_ratio_non_roll_mean: float | None
    sample_n_neighborhood: int
    sample_n_non_roll: int


def compute_roll_gaps(
    closes: Sequence[float],
    yymms: Sequence[str],
    timestamps: Sequence[datetime],
) -> tuple[RollGapRecord, ...]:
    """Detect rolls where yymm changes; gap uses prev close vs next open(=close)."""

    if not (len(closes) == len(yymms) == len(timestamps)):
        raise ValueError("closes、yymms、timestamps 长度必须一致")
    if len(closes) < 2:
        return ()

    records: list[RollGapRecord] = []
    for index in range(1, len(closes)):
        if yymms[index] == yymms[index - 1]:
            continue
        prev_close = float(closes[index - 1])
        next_open = float(closes[index])
        if prev_close == 0.0 or not math.isfinite(prev_close):
            raise ValueError("换月前收盘价非法")
        gap_abs = next_open - prev_close
        gap_rel = gap_abs / prev_close
        records.append(
            RollGapRecord(
                roll_index=index,
                timestamp=timestamps[index],
                from_yymm=str(yymms[index - 1]),
                to_yymm=str(yymms[index]),
                prev_close=prev_close,
                next_open=next_open,
                gap_abs=float(gap_abs),
                gap_rel=float(gap_rel),
            )
        )
    return tuple(records)


def neighborhood_mask(
    length: int,
    roll_indices: Sequence[int],
    window: int,
) -> np.ndarray:
    """True for bars within [roll-W, roll+W] inclusive around each roll index."""

    if window < 0:
        raise ValueError("window 必须非负")
    mask = np.zeros(length, dtype=bool)
    for roll_index in roll_indices:
        start = max(0, int(roll_index) - window)
        end = min(length, int(roll_index) + window + 1)
        mask[start:end] = True
    return mask


def _log_returns(closes: np.ndarray) -> np.ndarray:
    positive = closes[:-1] > 0
    safe = np.zeros(len(closes) - 1, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.diff(np.log(np.clip(closes, 1e-12, None)))
    safe[positive] = raw[positive]
    return safe


def summarize_roll_audit(
    *,
    closes: Sequence[float],
    gaps: Sequence[RollGapRecord],
    window: int,
    atr_ratios: Sequence[float | None] | None = None,
) -> RollAuditSummary:
    """Compute primary roll metrics and optional atr_ratio secondary means."""

    close_arr = np.asarray(closes, dtype=float)
    if close_arr.size < 2:
        raise ValueError("closes 至少需要 2 根 bar")

    roll_indices = tuple(gap.roll_index for gap in gaps)
    mask = neighborhood_mask(len(close_arr), roll_indices, window)
    # returns[i] corresponds to move from close[i] -> close[i+1]
    returns = _log_returns(close_arr)
    ret_mask = mask[1:]
    neighborhood_returns = returns[ret_mask]
    non_roll_returns = returns[~ret_mask]

    def _vol(values: np.ndarray) -> float:
        if values.size == 0:
            return float("nan")
        return float(np.std(values, ddof=0))

    def _p95_abs(values: np.ndarray) -> float:
        if values.size == 0:
            return float("nan")
        return float(np.percentile(np.abs(values), 95))

    neigh_vol = _vol(neighborhood_returns)
    non_vol = _vol(non_roll_returns)
    vol_ratio = (
        float(neigh_vol / non_vol)
        if math.isfinite(neigh_vol) and math.isfinite(non_vol) and non_vol > 0
        else float("nan")
    )
    neigh_p95 = _p95_abs(neighborhood_returns)
    non_p95 = _p95_abs(non_roll_returns)
    p95_ratio = (
        float(neigh_p95 / non_p95)
        if math.isfinite(neigh_p95) and math.isfinite(non_p95) and non_p95 > 0
        else float("nan")
    )

    gap_abs = np.asarray([gap.gap_abs for gap in gaps], dtype=float)
    gap_rel = np.asarray([gap.gap_rel for gap in gaps], dtype=float)

    atr_neigh_mean: float | None = None
    atr_non_mean: float | None = None
    if atr_ratios is not None:
        if len(atr_ratios) != len(close_arr):
            raise ValueError("atr_ratios 长度必须等于 closes")
        atr_arr = np.asarray(
            [np.nan if value is None else float(value) for value in atr_ratios],
            dtype=float,
        )
        neigh_vals = atr_arr[mask]
        non_vals = atr_arr[~mask]
        neigh_vals = neigh_vals[np.isfinite(neigh_vals)]
        non_vals = non_vals[np.isfinite(non_vals)]
        if neigh_vals.size:
            atr_neigh_mean = float(np.mean(neigh_vals))
        if non_vals.size:
            atr_non_mean = float(np.mean(non_vals))

    return RollAuditSummary(
        roll_count=len(gaps),
        gap_abs_mean=float(np.mean(np.abs(gap_abs))) if gap_abs.size else float("nan"),
        gap_abs_median=float(np.median(np.abs(gap_abs))) if gap_abs.size else float("nan"),
        gap_rel_mean=float(np.mean(np.abs(gap_rel))) if gap_rel.size else float("nan"),
        gap_rel_median=float(np.median(np.abs(gap_rel))) if gap_rel.size else float("nan"),
        neighborhood_vol=neigh_vol,
        non_roll_vol=non_vol,
        vol_ratio=vol_ratio,
        neighborhood_abs_return_p95=neigh_p95,
        non_roll_abs_return_p95=non_p95,
        abs_return_p95_ratio=p95_ratio,
        atr_ratio_neighborhood_mean=atr_neigh_mean,
        atr_ratio_non_roll_mean=atr_non_mean,
        sample_n_neighborhood=int(neighborhood_returns.size),
        sample_n_non_roll=int(non_roll_returns.size),
    )
