"""Build content-addressed deploy artifact set for DID/EI P1（research）.

Produces a deterministic file list + sha256 digests + aggregate set hash.
Does NOT claim Docker/OCI image digest（host has no docker in Delegation-50M）.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Research binding + lock surface（extend carefully; sorted for stability）
DEFAULT_PATHS = [
    "requirements.lock",
    "requirements.txt",
    "strategies/paaf/brooks_scalp_paaf_strategy.py",
    "strategies/paaf/brooks_scalp_paaf_strategy_v011.py",
    "strategies/paaf/brooks_scalp_paaf_strategy_v020.py",
    "strategies/paaf/detectors/brooks_scalp_first_pullback.py",
    "strategies/paaf/cxsd/__init__.py",
    "strategies/paaf/context_consumer/brooks_scalp_ctx_filter_v011.py",
]

OUT_JSON = ROOT / "docs" / "research" / "DID_CID_002_artifact_manifest_v2.json"
OUT_EVIDENCE = (
    ROOT / "research" / "output" / "evidence" / "DID_CID_002_V0_2" / "artifact_manifest.json"
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    files = []
    for rel in sorted(DEFAULT_PATHS):
        path = ROOT / rel
        if not path.is_file():
            print(f"MISSING {rel}", file=sys.stderr)
            return 2
        files.append({"path": rel.replace("\\", "/"), "sha256": _sha256_file(path)})

    canon = json.dumps(files, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    artifact_set_hash = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    payload = {
        "artifact_set_id": "DID_CID_002_V0_2_ARTIFACT_SET",
        "kind": "content_addressed_source_and_lock_bundle",
        "not_kind": ["oci_image_digest", "signed_release_tag"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "delegation": "Delegation-50M",
        "files": files,
        "artifact_set_hash": artifact_set_hash,
        "docker_available": False,
        "notes": "P1 strengthened packaging; container digest still OPEN",
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    OUT_JSON.write_text(text, encoding="utf-8")
    OUT_EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    OUT_EVIDENCE.write_text(text, encoding="utf-8")
    print(f"artifact_set_hash={artifact_set_hash}")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
