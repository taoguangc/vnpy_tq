"""Pure helpers for pre-registered roll-neighborhood annotations."""

from __future__ import annotations

from typing import Sequence

import numpy as np


DEFAULT_ROLL_WINDOW = 60


def roll_change_indices(contract_ids: Sequence[str]) -> tuple[int, ...]:
    """Return indices where the active contract changes."""

    return tuple(
        index
        for index in range(1, len(contract_ids))
        if contract_ids[index] != contract_ids[index - 1]
    )


def roll_neighborhood_mask(
    length: int,
    roll_indices: Sequence[int],
    window: int = DEFAULT_ROLL_WINDOW,
) -> np.ndarray:
    """Mark bars in each inclusive [roll-W, roll+W] neighborhood."""

    if isinstance(length, bool) or not isinstance(length, int) or length < 0:
        raise ValueError("length 必须是非负整数")
    if isinstance(window, bool) or not isinstance(window, int) or window < 0:
        raise ValueError("window 必须是非负整数")

    mask = np.zeros(length, dtype=bool)
    for roll_index in roll_indices:
        if (
            isinstance(roll_index, bool)
            or not isinstance(roll_index, int)
            or not 0 <= roll_index < length
        ):
            raise ValueError("roll_index 必须落在序列范围内")
        start = max(0, roll_index - window)
        end = min(length, roll_index + window + 1)
        mask[start:end] = True
    return mask


def contract_roll_neighborhood_mask(
    contract_ids: Sequence[str],
    window: int = DEFAULT_ROLL_WINDOW,
) -> np.ndarray:
    """Mark roll neighborhoods directly from active-contract identities."""

    indices = roll_change_indices(contract_ids)
    return roll_neighborhood_mask(len(contract_ids), indices, window)


def aggregate_roll_neighborhood(component_flags: Sequence[bool]) -> bool:
    """A composite bar is marked if any constituent 1m bar is marked."""

    if not component_flags:
        raise ValueError("component_flags 不得为空")
    if any(not isinstance(flag, (bool, np.bool_)) for flag in component_flags):
        raise TypeError("component_flags 必须只包含 bool")
    return any(bool(flag) for flag in component_flags)
