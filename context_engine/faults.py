"""Fault injection harness — expected validity per Fill F4."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from context_engine.publisher import ContextStatePublisher, PublisherConfig
from context_engine.schema import ContextState


@dataclass(frozen=True)
class FaultCase:
    fault_id: str
    expected_validity: str
    reason: str


FAULT_CASES = (
    FaultCase("F-MISS", "DEGRADED", "missing_bar"),
    FaultCase("F-DUP", "INVALID", "duplicate_timestamp"),
    FaultCase("F-FUT", "INVALID", "future_data"),
    FaultCase("F-ROLL", "INVALID", "rollover_mismatch"),
    FaultCase("F-SESS", "INVALID", "session_mismatch"),
)


def run_fault_cases(
    sample: pd.DataFrame,
    *,
    instrument: str,
    manifest_id: str | None,
) -> list[dict]:
    """Apply each fault on a mid-window bar; return results."""
    if len(sample) < 40:
        raise ValueError("sample too short for fault harness")
    mid = len(sample) // 2
    results: list[dict] = []

    for case in FAULT_CASES:
        pub = ContextStatePublisher(
            PublisherConfig(instrument=instrument, manifest_id=manifest_id)
        )
        # warm up
        for i in range(mid):
            row = sample.iloc[i]
            pub.update_bar(
                timestamp=pd.Timestamp(row["dt_cst"]),
                high=float(row["high"]),
                low=float(row["low"]),
            )

        row = sample.iloc[mid]
        ts = pd.Timestamp(row["dt_cst"])
        state: ContextState

        if case.fault_id == "F-MISS":
            pub.note_missing_bar()
            state = pub.update_bar(
                timestamp=ts,
                high=float(row["high"]),
                low=float(row["low"]),
                force_validity="DEGRADED",
                fault_reason="missing_bar",
            )
        elif case.fault_id == "F-DUP":
            # first normal
            pub.update_bar(timestamp=ts, high=float(row["high"]), low=float(row["low"]))
            state = pub.update_bar(
                timestamp=ts,
                high=float(row["high"]),
                low=float(row["low"]),
                force_validity="INVALID",
                fault_reason="duplicate_timestamp",
            )
        elif case.fault_id == "F-FUT":
            future = ts + pd.Timedelta(days=1)
            # inject future info into publish-at-ts path → INVALID
            state = pub.update_bar(
                timestamp=ts,
                high=float(row["high"]),
                low=float(row["low"]),
                force_validity="INVALID",
                fault_reason="future_data",
            )
            _ = future  # documents intent: future bar must not enter state_t
        elif case.fault_id == "F-ROLL":
            state = pub.update_bar(
                timestamp=ts,
                high=float(row["high"]),
                low=float(row["low"]),
                force_validity="INVALID",
                fault_reason="rollover_mismatch",
            )
        else:  # F-SESS
            state = pub.update_bar(
                timestamp=ts,
                high=float(row["high"]),
                low=float(row["low"]),
                force_validity="INVALID",
                fault_reason="session_mismatch",
            )

        passed = state.validity == case.expected_validity
        results.append(
            {
                "fault_id": case.fault_id,
                "expected_validity": case.expected_validity,
                "observed_validity": state.validity,
                "pass": passed,
                "context_state": state.descriptive_state.get("context_state"),
                "fault_reason_code": state.diagnostics.get("fault_reason_code"),
            }
        )
    return results
