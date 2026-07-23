"""RISK @0.2.0 + Context Filter F1 adapter for CID_003（CXSD-v0.1 gate）.

Does NOT mutate G5 binding bytes of strat_rev_opp16_01*.py.
Subclasses V020; F1 rule unchanged（expansion-only）.
Context permission only — sizing / kill remain on V020.
"""
from __future__ import annotations

from strategies.paaf.context_consumer.a1_published_state import (
    CONTEXT_VERSION,
    ENGINE_ID,
    SCHEMA_VERSION,
    publish_a1_context_state,
)
from strategies.paaf.cxsd import (
    CONTRACT_ID,
    build_audit_event,
    resolve_permission,
    validate_intent,
)
from strategies.paaf.strat_rev_opp16_01_v020 import StratRevOpp1601StrategyV020


class Opp16CtxFilterV020(StratRevOpp1601StrategyV020):
    """V020 capital controls + F1 expansion-only gate + CXSD audit."""

    filter_id = "F1_EXPANSION_ONLY"
    context_version = CONTEXT_VERSION
    cxsd_version = CONTRACT_ID
    consumer_id = "CI_FILTER_ADAPTER"
    surface_id = "RISK"
    freeze_id = "SIF_CID_003_V0_2_0"
    detector_binding = "OPP16@1.0.0"
    experiment_id = "CTX_CID003_EXP004"

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self._permission_denials: list[dict] = []
        self._cxsd_audit_events: list[dict] = []
        self._last_context_state = "invalid"
        self._last_cxsd_permission = "BLOCK"

    def on_init(self) -> None:
        self.write_log(
            f"{self.strategy_id}@0.2.0+F1+CXSD initialized "
            f"(Context×RISK adapter; parent bytes untouched; "
            f"engine={ENGINE_ID}; schema={SCHEMA_VERSION}; "
            f"context_version={CONTEXT_VERSION}; filter={self.filter_id}; "
            f"cxsd={self.cxsd_version}; experiment={self.experiment_id}; "
            f"surface={self.surface_id})"
        )
        self.load_bar(30)

    def _submit_stop_entry(self, result) -> None:
        validate_intent("get_state")
        validate_intent("decide")

        state = publish_a1_context_state(self.am)
        self._last_context_state = state
        filter_would_allow = state == "expansion"
        gate = resolve_permission(
            consumer_id=self.consumer_id,
            context_state=state,
            filter_would_allow=filter_would_allow,
        )
        self._last_cxsd_permission = gate.permission

        reason = getattr(result, "reason", None)
        direction = (
            result.direction.value
            if getattr(result, "direction", None) is not None
            else None
        )
        event_name = (
            "PERMISSION_ALLOW" if gate.permission == "ALLOW" else "PERMISSION_DENIAL"
        )
        audit = build_audit_event(
            experiment_id=self.experiment_id,
            surface_id=self.surface_id,
            context_state=state,
            permission=gate.permission,
            event=event_name,
            detector_binding=self.detector_binding,
            freeze_id=self.freeze_id,
            context_version=self.context_version,
            context_engine_id=ENGINE_ID,
            signal_reason=reason,
            extra={
                "filter_id": self.filter_id,
                "gate_reason": gate.reason,
                "direction": direction,
                "entry": getattr(result, "entry", None),
                "consumer_id": self.consumer_id,
            },
        )
        self._cxsd_audit_events.append(audit)

        if not gate.order_allowed:
            self._permission_denials.append(
                {
                    "event": "PERMISSION_DENIAL",
                    "context_state": state,
                    "filter_id": self.filter_id,
                    "cxsd_version": self.cxsd_version,
                    "permission": gate.permission,
                    "gate_reason": gate.reason,
                    "signal_reason": reason,
                    "direction": direction,
                    "entry": getattr(result, "entry", None),
                }
            )
            return
        super()._submit_stop_entry(result)
