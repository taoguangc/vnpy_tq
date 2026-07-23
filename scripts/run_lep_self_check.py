"""LEP self-check — fail-closed smoke for Delegation-50N."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.paaf.lep import CONTRACT_ID, gate_live, validate_vbp_pack


def main() -> int:
    template = json.loads(
        (ROOT / "docs" / "research" / "VBP_CID_002_venue_pack_TEMPLATE.json").read_text(
            encoding="utf-8"
        )
    )
    t = validate_vbp_pack(template, require_filled=False)
    live = gate_live(vbp_pack=template, vmp_checklist={}, claim_live=True)
    print(f"lep_contract={CONTRACT_ID}")
    print(f"template_ok={t.ok} reason={t.reason}")
    print(f"live_gate_on_template_ok={live.ok} reason={live.reason}")
    print(f"production_bindable={live.production_bindable} live_authorized={live.live_authorized}")
    if not t.ok or live.ok or live.production_bindable or live.live_authorized:
        return 1
    print("SELF_CHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
