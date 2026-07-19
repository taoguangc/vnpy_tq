"""Run OI_CHANGE_EXP001 Feature Artifact only."""

from __future__ import annotations

from paaf_scalar_feature_experiment import (
    ScalarExperimentConfig,
    run_artifact,
)

from strategies.paaf.sensors.oi_change import OIChangeSensor


CONFIG = ScalarExperimentConfig(
    experiment_id="OI_CHANGE_EXP001",
    run_id="OI_CHANGE_EXP001_RUN001",
    sensor_id="oi_change",
    sensor_version="1.0",
    artifact_id="OI_CHANGE_EXP001_FEATURES",
    evaluation_id="EVAL-OI-CHANGE-EXP001-001",
    evidence_id="EV-OI-CHANGE-EXP001-001",
    outcome_id="OUT-OI-CHANGE-EXP001-RV60",
    metric_full_id="MET-OI-CHANGE-EXP001-SPEARMAN-FULL",
    metric_ex_roll_id="MET-OI-CHANGE-EXP001-SPEARMAN-EX-ROLL",
    feature_key="oi_rel_change",
    input_key="open_interest",
    frame_column="open_interest",
    lookback=2,
    parameters={},
    hypothesis="oi_rel_change 与未来 RV_60 存在可检出关联（H0：无关联）",
)


if __name__ == "__main__":
    raise SystemExit(run_artifact(CONFIG, OIChangeSensor()))
