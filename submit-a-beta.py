from time import sleep

import click
import mlflow
# TODO I originally wanted to properly split submitter and runner dependencies
# but for now I'll allow this for simplicity's sake. It's needed to initialize
# mlflow.
from experiments import experiment_name

from slurm import get_dirs, submit

berbl_experiments = [
    "non_literal.generated_function",
    "non_literal.sparse_noisy_data",
    "non_literal.sine",
    "non_literal.variable_noise",
    "additional_non_literal.generated_function",
    "additional_non_literal.sparse_noisy_data",
]


@click.command()
@click.argument("NODE")
@click.option("-t",
              "--time",
              type=click.IntRange(min=10),
              default=120,
              help="Slurm's --time in minutes.",
              show_default=True)
@click.option("--mem",
              type=click.IntRange(min=1),
              default=1000,
              help="Slurm's --mem in megabytes.",
              show_default=True)
@click.option("--tracking-uri", type=str, default="mlruns")
def main(node, time, mem, tracking_uri):
    """
    Submits all experiments to NODE.
    """
    # Create experiments so we don't get races.
    mlflow.set_tracking_uri(tracking_uri)
    for module in berbl_experiments:
        mlflow.set_experiment(experiment_name("berbl", module))
        sleep(1)

    # TODO Put this into submit
    job_dir, results_dir = get_dirs()

    for module in berbl_experiments:
        for a_beta in [1e-2, 1e-1, 2e-2, 0.5, 1]:
            submit(
                node,
                time,
                mem,
                "berbl",
                module,
                job_dir=job_dir,
                results_dir=results_dir,
                standardize=False,
                tracking_uri=tracking_uri,
                n_reps=5,
                n_data_sets=5,
                params=f"--a-beta={a_beta}",
            )


if __name__ == "__main__":
    main()
