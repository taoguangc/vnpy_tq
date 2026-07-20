"""Run CLOSE_LOCATION_EXP001 Feature Artifact only."""

from __future__ import annotations

from paaf_scalar_feature_experiment import (
    ScalarExperimentConfig,
    run_artifact,
)

from strategies.paaf.sensors.close_location import CloseLocationSensor


CONFIG = ScalarExperimentConfig(
    experiment_id="CLOSE_LOCATION_EXP001",
    run_id="CLOSE_LOCATION_EXP001_RUN001",
    sensor_id="close_location",
    sensor_version="1.0",
    artifact_id="CLOSE_LOCATION_EXP001_FEATURES",
    evaluation_id="EVAL-CLOSE-LOCATION-EXP001-001",
    evidence_id="EV-CLOSE-LOCATION-EXP001-001",
    outcome_id="OUT-CLOSE-LOCATION-EXP001-SR60",
    metric_full_id="MET-CLOSE-LOCATION-EXP001-SPEARMAN-FULL",
    metric_ex_roll_id="MET-CLOSE-LOCATION-EXP001-SPEARMAN-EX-ROLL",
    feature_key="close_location",
    input_key="",
    frame_column="",
    lookback=1,
    parameters={},
    hypothesis=(
        "close_location 与未来 SR_60（signed log-return 之和）"
        "存在可检出关联（H0：无关联）"
    ),
    window_mode="ohlc",
    outcome_kind="signed_sum",
    outcome_label="SR_60",
)


if __name__ == "__main__":
    raise SystemExit(run_artifact(CONFIG, CloseLocationSensor()))
