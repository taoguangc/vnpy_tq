"""Public contracts for the PAAF Evidence Engine."""

from strategies.paaf.evidence.hashing import (
    canonical_json_dumps,
    hash_bytes,
    hash_canonical_json,
    hash_file,
)
from strategies.paaf.evidence.models import (
    ArtifactReference,
    EvidenceRecord,
    ExperimentManifest,
)
from strategies.paaf.evidence.provenance import (
    build_observation_key,
    fingerprint_evidence_body,
    fingerprint_manifest,
    fingerprint_parameters,
    verify_parameter_fingerprint,
)
from strategies.paaf.evidence.repository import (
    DEFAULT_EVIDENCE_ROOT,
    EvidenceRepository,
)

__all__ = [
    "ArtifactReference",
    "DEFAULT_EVIDENCE_ROOT",
    "EvidenceRecord",
    "EvidenceRepository",
    "ExperimentManifest",
    "build_observation_key",
    "canonical_json_dumps",
    "fingerprint_evidence_body",
    "fingerprint_manifest",
    "fingerprint_parameters",
    "hash_bytes",
    "hash_canonical_json",
    "hash_file",
    "verify_parameter_fingerprint",
]
