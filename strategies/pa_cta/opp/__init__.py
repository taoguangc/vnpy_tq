# -*- coding: utf-8 -*-
"""pa_cta OPP mixins package."""
from __future__ import annotations

from strategies.pa_cta.opp.opp02 import Opp02Mixin
from strategies.pa_cta.opp.opp08 import Opp08Mixin
from strategies.pa_cta.opp.opp12 import Opp12Mixin
from strategies.pa_cta.opp.opp13 import Opp13Mixin
from strategies.pa_cta.opp.opp15 import Opp15Mixin
from strategies.pa_cta.opp.opp16 import Opp16Mixin
from strategies.pa_cta.opp.opp17 import Opp17Mixin
from strategies.pa_cta.opp.opp19 import Opp19Mixin


class OppMixins(
    Opp08Mixin,
    Opp16Mixin,
    Opp02Mixin,
    Opp12Mixin,
    Opp13Mixin,
    Opp15Mixin,
    Opp17Mixin,
    Opp19Mixin,
):
    """组合全部 OPP Mixin，供 BrooksPaCtaStrategy 继承。"""


__all__ = ["OppMixins"]
