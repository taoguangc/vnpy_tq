"""Run OPP16_EXP001 detection Artifact only."""

from paaf_opp16_event_experiment import CONFIG, run_artifact


if __name__ == "__main__":
    raise SystemExit(run_artifact(CONFIG))
