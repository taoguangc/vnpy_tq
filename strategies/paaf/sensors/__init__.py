"""Public Feature Sensor Framework contracts."""

from strategies.paaf.sensors.artifact import write_feature_artifact
from strategies.paaf.sensors.atr_compression import (
    ATR_COMPRESSION_DESCRIPTOR,
    ATR_OUTPUT_KEY,
    ATR_SENSOR_ID,
    ATR_SENSOR_VERSION,
    ATRCompressionSensor,
)
from strategies.paaf.sensors.base import BaseFeatureSensor
from strategies.paaf.sensors.demo_constant import (
    DEMO_CONSTANT_DESCRIPTOR,
    DEMO_OUTPUT_KEY,
    DEMO_SENSOR_ID,
    DEMO_SENSOR_VERSION,
    DemoConstantSensor,
)
from strategies.paaf.sensors.models import (
    FeatureResult,
    SensorCapability,
    SensorDescriptor,
    SensorStatus,
)
from strategies.paaf.sensors.registry import (
    SensorRegistry,
    build_sensor_registry,
)
from strategies.paaf.sensors.volume_ratio import (
    DEFAULT_VOLUME_BASELINE_WINDOW,
    VOLUME_OUTPUT_KEY,
    VOLUME_RATIO_DESCRIPTOR,
    VOLUME_SENSOR_ID,
    VOLUME_SENSOR_VERSION,
    VolumeRatioSensor,
)

__all__ = [
    "ATR_COMPRESSION_DESCRIPTOR",
    "ATR_OUTPUT_KEY",
    "ATR_SENSOR_ID",
    "ATR_SENSOR_VERSION",
    "ATRCompressionSensor",
    "DEMO_CONSTANT_DESCRIPTOR",
    "DEMO_OUTPUT_KEY",
    "DEMO_SENSOR_ID",
    "DEMO_SENSOR_VERSION",
    "BaseFeatureSensor",
    "DemoConstantSensor",
    "FeatureResult",
    "SensorCapability",
    "SensorDescriptor",
    "SensorRegistry",
    "SensorStatus",
    "DEFAULT_VOLUME_BASELINE_WINDOW",
    "VOLUME_OUTPUT_KEY",
    "VOLUME_RATIO_DESCRIPTOR",
    "VOLUME_SENSOR_ID",
    "VOLUME_SENSOR_VERSION",
    "VolumeRatioSensor",
    "build_sensor_registry",
    "write_feature_artifact",
]
