# -*- coding: utf-8 -*-
from strategies.pa_minimal.detectors.schema import PatternMatch
from strategies.pa_minimal.detectors.opp02 import match_opp02
from strategies.pa_minimal.detectors.opp08 import match_opp08
from strategies.pa_minimal.detectors.opp12 import match_opp12
from strategies.pa_minimal.detectors.opp13 import match_opp13_boundary, match_opp13_double_top
from strategies.pa_minimal.detectors.opp15 import match_opp15_trigger
from strategies.pa_minimal.detectors.opp16 import match_opp16
from strategies.pa_minimal.detectors.opp17 import match_opp17
from strategies.pa_minimal.detectors.opp19 import match_opp19

__all__ = [
    "PatternMatch",
    "match_opp02",
    "match_opp08",
    "match_opp12",
    "match_opp13_boundary",
    "match_opp13_double_top",
    "match_opp15_trigger",
    "match_opp16",
    "match_opp17",
    "match_opp19",
]
