"""Run VOLUME_RATIO_EXP001 Feature Artifact only."""

from __future__ import annotations

from paaf_scalar_feature_experiment import (
    ScalarExperimentConfig,
    run_artifact,
)

from strategies.paaf.sensors.volume_ratio import (
    DEFAULT_VOLUME_BASELINE_WINDOW,
    VolumeRatioSensor,
)


CONFIG = ScalarExperimentConfig(
    experiment_id="VOLUME_RATIO_EXP001",
    run_id="VOLUME_RATIO_EXP001_RUN001",
    sensor_id="volume_ratio",
    sensor_version="1.0",
    artifact_id="VOLUME_RATIO_EXP001_FEATURES",
    evaluation_id="EVAL-VOLUME-RATIO-EXP001-001",
    evidence_id="EV-VOLUME-RATIO-EXP001-001",
    outcome_id="OUT-VOLUME-RATIO-EXP001-RV60",
    metric_full_id="MET-VOLUME-RATIO-EXP001-SPEARMAN-FULL",
    metric_ex_roll_id="MET-VOLUME-RATIO-EXP001-SPEARMAN-EX-ROLL",
    feature_key="volume_ratio",
    input_key="volume",
    frame_column="volume",
    lookback=DEFAULT_VOLUME_BASELINE_WINDOW,
    parameters={"baseline_window": DEFAULT_VOLUME_BASELINE_WINDOW},
    hypothesis="volume_ratio 与未来 RV_60 存在可检出关联（H0：无关联）",
)


if __name__ == "__main__":
    raise SystemExit(run_artifact(CONFIG, VolumeRatioSensor()))
