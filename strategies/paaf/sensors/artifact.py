"""FeatureResult artifact writer; separate from EvidenceRepository."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from strategies.paaf.evidence.hashing import canonical_json_dumps, hash_file
from strategies.paaf.evidence.models import ArtifactReference
from strategies.paaf.sensors.models import FeatureResult


def write_feature_artifact(
    path: Path,
    results: Iterable[FeatureResult],
    *,
    artifact_id: str,
    uri: str,
) -> ArtifactReference:
    """Write immutable JSONL observations and return their reference."""

    observations = tuple(results)
    if not observations:
        raise ValueError("Feature artifact 至少需要一个 FeatureResult")
    if any(not isinstance(item, FeatureResult) for item in observations):
        raise TypeError("results 只允许 FeatureResult")

    content = "".join(
        f"{canonical_json_dumps(item.to_dict())}\n"
        for item in observations
    )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as file:
        file.write(content)

    return ArtifactReference(
        artifact_id=artifact_id,
        uri=uri,
        content_hash=hash_file(target),
        artifact_type="feature_results",
    )
