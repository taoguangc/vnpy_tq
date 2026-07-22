"""MECH @0.1.1 + Context Filter F1 adapter（CTX_CID002_EXP001）.

Does NOT mutate G5 binding bytes of brooks_scalp_paaf_strategy*.py.
Subclasses V011 and gates stop-entry proposals by A1 ContextState.
"""
from __future__ import annotations

from strategies.paaf.brooks_scalp_paaf_strategy_v011 import BrooksScalpPaafStrategyV011
from strategies.paaf.context_consumer.a1_published_state import (
    CONTEXT_VERSION,
    ENGINE_ID,
    SCHEMA_VERSION,
    publish_a1_context_state,
)


class BrooksScalpCtxFilterV011(BrooksScalpPaafStrategyV011):
    """V011 orchestration + F1 expansion-only permission gate."""

    filter_id = "F1_EXPANSION_ONLY"
    context_version = CONTEXT_VERSION

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self._permission_denials: list[dict] = []
        self._last_context_state = "invalid"

    def on_init(self) -> None:
        self.write_log(
            f"{self.strategy_id}@0.1.1+F1 initialized "
            f"(Context Filter adapter; parent bytes untouched; "
            f"engine={ENGINE_ID}; schema={SCHEMA_VERSION}; "
            f"context_version={CONTEXT_VERSION}; filter={self.filter_id})"
        )
        self.load_bar(30)

    def _submit_stop_entry(self, result) -> None:
        state = publish_a1_context_state(self.am)
        self._last_context_state = state
        if state != "expansion":
            self._permission_denials.append(
                {
                    "event": "PERMISSION_DENIAL",
                    "context_state": state,
                    "filter_id": self.filter_id,
                    "signal_reason": getattr(result, "reason", None),
                    "direction": (
                        result.direction.value
                        if getattr(result, "direction", None) is not None
                        else None
                    ),
                    "entry": getattr(result, "entry", None),
                    "datetime": getattr(getattr(self, "am", None), "datetime", None),
                }
            )
            # Prefer bar datetime from am if available via last update — harness fills later
            return
        super()._submit_stop_entry(result)
