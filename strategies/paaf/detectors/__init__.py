"""PAAF Detector 实现。

真实 OPP 文件名冻结为 ``oppXX_<slug>.py``。
``DEMO_*`` 只用于框架验证，不属于 Opportunity Library Alpha。
"""

from strategies.paaf.detectors.demo_minimal import (
    DEMO_MINIMAL_DESCRIPTOR,
    DemoMinimalDetector,
)

__all__ = [
    "DEMO_MINIMAL_DESCRIPTOR",
    "DemoMinimalDetector",
]
