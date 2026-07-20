"""PAAF Detector 实现。

真实 OPP 文件名冻结为 ``oppXX_<slug>.py``。
``DEMO_*`` 只用于框架验证，不属于 Opportunity Library Alpha。
"""

from strategies.paaf.detectors.demo_minimal import (
    DEMO_MINIMAL_DESCRIPTOR,
    DemoMinimalDetector,
)
from strategies.paaf.detectors.opp16_two_bar_reversal import (
    DEFAULT_BODY_RATIO,
    OPP16_DESCRIPTOR,
    OPP16_DETECTOR_ID,
    OPP16_DETECTOR_VERSION,
    OPP16_OPPORTUNITY_ID,
    OPP16TwoBarReversalDetector,
)

__all__ = [
    "DEMO_MINIMAL_DESCRIPTOR",
    "DemoMinimalDetector",
    "DEFAULT_BODY_RATIO",
    "OPP16_DESCRIPTOR",
    "OPP16_DETECTOR_ID",
    "OPP16_DETECTOR_VERSION",
    "OPP16_OPPORTUNITY_ID",
    "OPP16TwoBarReversalDetector",
]
