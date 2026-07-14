# -*- coding: utf-8
"""向后兼容：hc setup 细读 → run_setup_tm_detail --symbol hc。"""
from research.run_setup_tm_detail import analyze_symbol

if __name__ == "__main__":
    analyze_symbol("hc")
