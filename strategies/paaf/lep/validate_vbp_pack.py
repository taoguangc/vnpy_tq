"""Validate VBP venue packs（TEMPLATE vs FILLED）."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from strategies.paaf.lep.constants import (
    BACKTEST_FILL_BINDING,
    LRC_CONTRACT_ID,
    VBP_FILLED_REQUIRED_FIELDS,
    VBP_PROTOCOL_ID,
)


@dataclass(frozen=True)
class VbpCheck:
    ok: bool
    reason: str
    kind: str


def validate_vbp_pack(pack: dict[str, Any] | None, *, require_filled: bool = False) -> VbpCheck:
    if not isinstance(pack, dict):
        return VbpCheck(False, "pack_missing_or_not_object", "UNKNOWN")

    protocol = str(pack.get("protocol_id") or "").strip()
    if protocol != VBP_PROTOCOL_ID:
        return VbpCheck(False, "protocol_id_mismatch", str(pack.get("kind") or "UNKNOWN"))

    kind = str(pack.get("kind") or "").strip().upper()
    filled = bool(pack.get("filled"))

    if kind == "TEMPLATE":
        if filled:
            return VbpCheck(False, "template_must_have_filled_false", kind)
        if require_filled:
            return VbpCheck(False, "live_requires_filled_pack", kind)
        return VbpCheck(True, "template_ok", kind)

    if kind != "FILLED":
        return VbpCheck(False, "kind_must_be_template_or_filled", kind or "UNKNOWN")

    if not filled:
        return VbpCheck(False, "filled_kind_requires_filled_true", kind)

    for field in VBP_FILLED_REQUIRED_FIELDS:
        value = pack.get(field)
        if value is None or value == "" or value == []:
            return VbpCheck(False, f"missing_field:{field}", kind)

    account_class = str(pack.get("account_class") or "").strip().upper()
    if account_class not in {"SIM", "FUNDED"}:
        return VbpCheck(False, "account_class_must_be_sim_or_funded", kind)

    fill_binding = str(pack.get("fill_binding_id") or "").strip()
    if fill_binding == BACKTEST_FILL_BINDING:
        return VbpCheck(False, "fill_binding_must_not_be_backtest_defaults", kind)

    if str(pack.get("lrc_contract_id") or "").strip() != LRC_CONTRACT_ID:
        return VbpCheck(False, "lrc_contract_id_mismatch", kind)

    return VbpCheck(True, "filled_ok", kind)
