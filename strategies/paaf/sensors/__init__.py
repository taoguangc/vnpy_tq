"""Public Feature Sensor Framework contracts."""

from strategies.paaf.sensors.artifact import write_feature_artifact
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

__all__ = [
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
    "build_sensor_registry",
    "write_feature_artifact",
]
