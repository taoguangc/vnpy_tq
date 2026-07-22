"""PAAF Detector 实现。

真实 OPP 文件名冻结为 ``oppXX_<slug>.py``。
``DEMO_*`` 只用于框架验证，不属于 Opportunity Library Alpha。
"""

from strategies.paaf.detectors.brooks_scalp_first_pullback import (
    BROOKS_SCALP_FP_DESCRIPTOR,
    BrooksScalpFirstPullbackDetector,
    DETECTOR_ID as BROOKS_SCALP_FP_ID,
    DETECTOR_VERSION as BROOKS_SCALP_FP_VERSION,
    OPPORTUNITY_ID as BROOKS_SCALP_FP_OPPORTUNITY_ID,
)
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
    "BROOKS_SCALP_FP_DESCRIPTOR",
    "BROOKS_SCALP_FP_ID",
    "BROOKS_SCALP_FP_OPPORTUNITY_ID",
    "BROOKS_SCALP_FP_VERSION",
    "BrooksScalpFirstPullbackDetector",
    "DEMO_MINIMAL_DESCRIPTOR",
    "DemoMinimalDetector",
    "DEFAULT_BODY_RATIO",
    "OPP16_DESCRIPTOR",
    "OPP16_DETECTOR_ID",
    "OPP16_DETECTOR_VERSION",
    "OPP16_OPPORTUNITY_ID",
    "OPP16TwoBarReversalDetector",
]
