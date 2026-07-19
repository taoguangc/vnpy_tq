"""Run OI_CHANGE_EXP001 Evaluation only."""

from run_oi_change_exp001 import CONFIG

from paaf_scalar_feature_experiment import run_evaluation


if __name__ == "__main__":
    raise SystemExit(run_evaluation(CONFIG))
