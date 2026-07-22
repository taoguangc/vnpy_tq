"""Implementation smoke test — synthetic bars only; NOT Observation / Evidence."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from context_engine.publisher import publish_batch, publish_streaming  # noqa: E402
from context_engine.schema import ContextState, schema_document  # noqa: E402


def _synthetic(n: int = 50) -> pd.DataFrame:
    idx = pd.date_range("2024-01-02 09:00", periods=n, freq="min", tz="Asia/Shanghai")
    # alternating narrow/wide ranges
    high = [100.0 + (0.2 if i % 3 else 2.0) for i in range(n)]
    low = [100.0 - (0.2 if i % 3 else 2.0) for i in range(n)]
    close = [(h + l) / 2 for h, l in zip(high, low)]
    return pd.DataFrame({"dt_cst": idx, "high": high, "low": low, "close": close, "volume": 1.0})


def main() -> int:
    df = _synthetic()
    a = publish_batch(df, instrument="TEST", manifest_id="smoke")
    b = publish_streaming(df, instrument="TEST", manifest_id="smoke")
    assert len(a) == len(b) == len(df)
    for sa, sb in zip(a, b):
        assert sa.exact_key() == sb.exact_key()
        assert sa.confidence == sb.confidence
        assert isinstance(sa, ContextState)
        assert "context_state" in sa.descriptive_state
        assert sa.descriptive_state["context_state"] in {
            "compression",
            "expansion",
            "invalid",
        }
    # forbidden diagnostics
    try:
        ContextState(
            timestamp="t",
            instrument="x",
            context_version="A1-CTX-PS-v1.0.0",
            validity="VALID",
            descriptive_state={"context_state": "compression"},
            confidence=1.0,
            diagnostics={"expected_direction": "long"},
        )
        raise AssertionError("forbidden diagnostics should fail")
    except ValueError:
        pass
    doc = schema_document()
    assert doc["confidence_semantics"] == "computational_confidence_only"
    print("[smoke] PASS — batch==streaming; schema OK; no Observation", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
