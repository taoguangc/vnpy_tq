"""Run OPP16_EXP001 Evaluation only."""

from paaf_opp16_event_experiment import CONFIG, run_evaluation


if __name__ == "__main__":
    raise SystemExit(run_evaluation(CONFIG))
