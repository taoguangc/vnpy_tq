"""Experiment Workflow Phase 1 contract tests."""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

from strategies.paaf.evidence import (
    EvidenceRepository,
    ExperimentContext,
    ExperimentWorkflow,
    RunContext,
    register_artifact_reference,
)


CREATED_AT = datetime(2026, 7, 19, 10, 0, tzinfo=timezone.utc)
ARTIFACT_URI = "artifacts/features-001/features.parquet"
ARTIFACT_HASH = "sha256:fixture"


def _context(
    *,
    experiment_id: str = "EXP-001",
    parameters: dict[str, str | int | float | bool] | None = None,
) -> ExperimentContext:
    return ExperimentContext(
        experiment_id=experiment_id,
        sensor_id="fixture_sensor",
        sensor_version="1.0",
        parameters=(
            parameters
            if parameters is not None
            else {"window": 14, "normalize": True}
        ),
        hypothesis="Fixture observation precedes fixture outcome.",
        code_revision="git:abc",
        data_fingerprint="sha256:data",
        environment_fingerprint="sha256:env",
        data_protocol_version="fixture-v1",
    )


def _run(
    experiment_id: str = "EXP-001",
    run_id: str | None = None,
) -> RunContext:
    return RunContext(
        experiment_id=experiment_id,
        created_at=CREATED_AT,
        run_id=run_id,
        labels={"purpose": "contract-test"},
    )


def _artifact():
    return register_artifact_reference(
        artifact_id="features-001",
        uri=ARTIFACT_URI,
        content_hash=ARTIFACT_HASH,
        artifact_type="feature_results",
    )


class TestWorkflowContexts(unittest.TestCase):
    def test_contexts_are_immutable_and_mappings_are_readonly(self) -> None:
        context = _context()
        run = _run(run_id="RUN-002")

        with self.assertRaises(FrozenInstanceError):
            context.sensor_version = "2.0"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            context.parameters["window"] = 20  # type: ignore[index]
        with self.assertRaises(TypeError):
            run.labels["purpose"] = "changed"  # type: ignore[index]
        self.assertEqual(run.run_id, "RUN-002")

    def test_run_id_is_optional_but_caller_owned(self) -> None:
        self.assertIsNone(_run().run_id)
        with self.assertRaisesRegex(ValueError, "run_id"):
            _run(run_id=" ")

    def test_run_context_requires_timezone(self) -> None:
        with self.assertRaisesRegex(ValueError, "时区"):
            RunContext(
                experiment_id="EXP-001",
                created_at=datetime(2026, 7, 19, 10, 0),
            )


class TestExperimentWorkflow(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = EvidenceRepository(Path(self.temp_dir.name))
        self.workflow = ExperimentWorkflow(self.repository)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_manifest_parameter_fingerprint_ignores_key_order(self) -> None:
        left = self.workflow.build_manifest(
            _context(parameters={"window": 14, "normalize": True}),
            (_artifact(),),
        )
        right = self.workflow.build_manifest(
            _context(parameters={"normalize": True, "window": 14}),
            (_artifact(),),
        )
        self.assertEqual(
            left.parameter_fingerprint,
            right.parameter_fingerprint,
        )

    def test_full_ordered_workflow_persists_and_replays(self) -> None:
        context = _context()
        manifest = self.workflow.build_manifest(context, (_artifact(),))
        self.workflow.persist_manifest(manifest)

        evidence = self.workflow.build_evidence(
            context,
            run_context=_run(run_id="RUN-001"),
            evidence_id="EV-001",
            decision="HOLD",
            feature_artifact_uri=ARTIFACT_URI,
            artifact_hash=ARTIFACT_HASH,
            observation={"fixture_score": 0.5},
            outcome={"future_value": 0.7},
            window={"bars_forward": 30},
            metrics={"sample_n": 10.0},
            metadata={"author": "caller"},
        )
        self.workflow.persist_evidence(evidence)

        loaded_manifest, loaded_evidence = self.workflow.replay(
            "EXP-001",
            "EV-001",
        )
        self.assertEqual(loaded_manifest, manifest)
        self.assertEqual(loaded_evidence, evidence)
        self.assertEqual(loaded_manifest.sensor_version, "1.0")
        self.assertEqual(loaded_manifest.code_revision, "git:abc")
        self.assertEqual(loaded_manifest.data_fingerprint, "sha256:data")
        self.assertEqual(loaded_evidence.created_at, CREATED_AT)
        self.assertEqual(loaded_evidence.metadata, {"author": "caller"})
        self.assertNotIn("purpose", loaded_evidence.metadata)
        self.assertNotIn("run_id", loaded_evidence.metadata)

    def test_build_evidence_before_persist_manifest_fails(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.workflow.build_evidence(
                _context(),
                run_context=_run(),
                evidence_id="EV-001",
                decision="HOLD",
                feature_artifact_uri=ARTIFACT_URI,
                artifact_hash=ARTIFACT_HASH,
            )

    def test_build_evidence_does_not_auto_save_manifest(self) -> None:
        context = _context()
        self.workflow.build_manifest(context, (_artifact(),))

        with self.assertRaises(FileNotFoundError):
            self.workflow.build_evidence(
                context,
                run_context=_run(),
                evidence_id="EV-001",
                decision="HOLD",
                feature_artifact_uri=ARTIFACT_URI,
                artifact_hash=ARTIFACT_HASH,
            )
        self.assertFalse(self.repository.manifest_exists("EXP-001"))

    def test_run_and_experiment_ids_must_match(self) -> None:
        context = _context()
        self.workflow.persist_manifest(
            self.workflow.build_manifest(context, (_artifact(),))
        )

        with self.assertRaisesRegex(ValueError, "RunContext.experiment_id"):
            self.workflow.build_evidence(
                context,
                run_context=_run("EXP-OTHER"),
                evidence_id="EV-001",
                decision="HOLD",
                feature_artifact_uri=ARTIFACT_URI,
                artifact_hash=ARTIFACT_HASH,
            )

    def test_evidence_requires_registered_artifact_reference(self) -> None:
        context = _context()
        self.workflow.persist_manifest(
            self.workflow.build_manifest(context)
        )

        with self.assertRaisesRegex(ValueError, "未在 Manifest"):
            self.workflow.build_evidence(
                context,
                run_context=_run(),
                evidence_id="EV-001",
                decision="HOLD",
                feature_artifact_uri=ARTIFACT_URI,
                artifact_hash=ARTIFACT_HASH,
            )

    def test_persist_is_append_only(self) -> None:
        manifest = self.workflow.build_manifest(_context(), (_artifact(),))
        self.workflow.persist_manifest(manifest)
        with self.assertRaises(FileExistsError):
            self.workflow.persist_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
