"""Export a fail-closed LEP compliance bundle from the VBP TEMPLATE.

Demonstrates evidence export; TEMPLATE must FAIL claim_live gate.
≠ Production Bindable · ≠ go-live.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from strategies.paaf.lep import build_and_export, default_evidence_dir


def main() -> int:
    template = json.loads(
        (ROOT / "docs" / "research" / "VBP_CID_002_venue_pack_TEMPLATE.json").read_text(
            encoding="utf-8"
        )
    )
    out = default_evidence_dir(ROOT, "LEP_CID_002_BUNDLE_001")
    meta = build_and_export(
        out,
        vbp_pack=template,
        vmp_checklist={},
        claim_live=True,
        run_id="LEP_CID_002_BUNDLE_001",
        note="TEMPLATE under live claim → expect gate_ok=false",
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    if meta["gate_ok"] or meta["production_bindable"] or meta["live_authorized"]:
        return 1
    print(f"WROTE {out}")
    print("EXPORT_SELF_CHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
