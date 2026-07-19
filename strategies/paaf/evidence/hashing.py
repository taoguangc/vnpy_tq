"""Deterministic hashing helpers for Evidence Engine Phase 0."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


def hash_bytes(content: bytes) -> str:
    """Return stable ``sha256:<hex>`` fingerprint for raw bytes."""

    digest = hashlib.sha256(content).hexdigest()
    return f"sha256:{digest}"


def hash_file(path: Path | str) -> str:
    """Hash file content; path itself is not part of the fingerprint."""

    return hash_bytes(Path(path).read_bytes())


def canonical_json_dumps(payload: Mapping[str, Any] | list[Any] | Any) -> str:
    """Serialize JSON with sorted keys and stable separators."""

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def hash_canonical_json(payload: Mapping[str, Any] | list[Any] | Any) -> str:
    """Hash canonical UTF-8 JSON bytes of ``payload``."""

    return hash_bytes(canonical_json_dumps(payload).encode("utf-8"))
