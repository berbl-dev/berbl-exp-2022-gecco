import os
import pathlib
import shutil
import tempfile
from subprocess import PIPE, Popen
from time import sleep
from datetime import datetime

import mlflow
import click

# TODO I originally wanted to properly split submitter and runner dependencies
# but for now I'll allow this for simplicity's sake.
from experiments import experiment_name

seed0 = 0
data_seed0 = 0

# Name of task and whether soft interval matching is used.
berbl_experiments = [
    "book.generated_function",
    "book.sparse_noisy_data",
    "book.sine",
    "book.variable_noise",
    # Not in the book but required for fairer comparison with XCSF.
    "additional_literal.generated_function",
    "additional_literal.sparse_noisy_data",
    # Expected to behave the same as the literal implementation.
    "non_literal.generated_function",
    "non_literal.sparse_noisy_data",
    "non_literal.sine",
    "non_literal.variable_noise",
    # Not in the book but required for fairer comparison with XCSF.
    "additional_non_literal.generated_function",
    "additional_non_literal.sparse_noisy_data",
]
xcsf_experiments = [
    "book.generated_function",
    "book.sparse_noisy_data",
    "book.sine",
    "book.variable_noise",
]


def get_dirs():
    job_dir = os.getcwd()
    datetime_ = datetime.now().isoformat()
    results_dir = f"{job_dir}/results/{datetime_}"
    os.makedirs(f"{results_dir}/output", exist_ok=True)
    os.makedirs(f"{results_dir}/jobs", exist_ok=True)
    return job_dir, results_dir


@click.group()
def main():
    pass


def submit(node,
           time,
           mem,
           algorithm,
           module,
           standardize,
           job_dir,
           results_dir,
           tracking_uri,
           params="",
           n_reps=5,
           n_data_sets=5):
    """
    Submit one ``single(…)`` job to the cluster for each repetition.
    """

    njobs = n_reps * n_data_sets

    standardize_option = '--standardize' if standardize else '--no-standardize'
    sbatch = "\n".join([
        f'#!/usr/bin/env bash',  #
        f'#SBATCH --nodelist={node}',
        f'#SBATCH --time={time}',
        f'#SBATCH --mem={mem}',
        f'#SBATCH --partition=cpu',
        f'#SBATCH --output="{results_dir}/output/output-%A-%a.txt"',
        f'#SBATCH --array=0-{njobs - 1}',
        (
            # NOTE `nixx` is the nix command with enabled flake support on the
            # servers.
            # provide job_dir to create the environment
            f'nixx develop "{job_dir}" --command '
            # provide job_dir to add job_dir/src to PYTHONPATH
            f'./run "{job_dir}" '
            f'{algorithm} '
            f'{module} '
            f'{standardize_option} '
            # NOTE / is integer division in bash.
            f'--seed=$(({seed0} + $SLURM_ARRAY_TASK_ID / {n_data_sets})) '
            f'--data-seed=$(({data_seed0} + $SLURM_ARRAY_TASK_ID % {n_data_sets})) '
            '--run-name=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID} '
            f'--tracking-uri="{results_dir}/{tracking_uri}" '
            f'{params}\n')
    ])
    print(sbatch)
    print()

    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, "w+") as f:
        f.write(sbatch)
    print(f"Wrote sbatch to {tmp.name}.")
    print()

    p = Popen(["sbatch", f"{tmp.name}"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    output = p.communicate()
    stdout = output[0].decode("utf-8")
    stderr = output[1].decode("utf-8")
    print(f"stdout:\n{stdout}\n")
    print(f"stderr:\n{stderr}\n")
    jobid = int(stdout.replace("Submitted batch job ", ""))
    print(f"Job ID: {jobid}")
    print()

    sbatch_dir = f"{results_dir}/jobs"
    os.makedirs(sbatch_dir, exist_ok=True)
    tmppath = pathlib.Path(tmp.name)
    fname = pathlib.Path(sbatch_dir, f"{jobid}.sbatch")
    shutil.copy(tmppath, fname)
    print(f"Renamed {tmp.name} to {fname}")


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
def slurm(node, time, mem, tracking_uri):
    """
    Submits all experiments to NODE.
    """
    # Create experiments so we don't get races.
    mlflow.set_tracking_uri(tracking_uri)
    for module in berbl_experiments:
        mlflow.set_experiment(experiment_name("berbl", module))
        sleep(0.5)
    for module in xcsf_experiments:
        mlflow.set_experiment(experiment_name("xcsf", module))
        sleep(0.5)

    job_dir, results_dir = get_dirs()

    for module in berbl_experiments:
        submit(node,
               time,
               mem,
               "berbl",
               module,
               job_dir=job_dir,
               results_dir=results_dir,
               standardize=False,
               tracking_uri=tracking_uri,
               n_reps=10,
               n_data_sets=10)
        submit(node,
               time,
               mem,
               "berbl",
               module,
               job_dir=job_dir,
               results_dir=results_dir,
               standardize=True,
               tracking_uri=tracking_uri,
               n_reps=10,
               n_data_sets=10)
    for module in xcsf_experiments:
        submit(node,
               time,
               mem,
               "xcsf",
               module,
               job_dir=job_dir,
               results_dir=results_dir,
               standardize=True,
               tracking_uri=tracking_uri,
               n_reps=10,
               n_data_sets=10)


@click.command()
@click.argument("NODE")
@click.argument("ALGORITHM")
@click.argument("MODULE")
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
@click.option("--standardize/--no-standardize",
              type=bool,
              default=False,
              show_default=True)
@click.option("--tracking-uri", type=str, default="mlruns")
def slurm1(node, algorithm, module, time, mem, standardize, tracking_uri):
    """
    Submits a single experiment (running ALGORITHM on task MODULE) to NODE.
    """
    job_dir, results_dir = get_dirs()

    submit(node,
           time,
           mem,
           algorithm,
           module,
           job_dir=job_dir,
           results_dir=results_dir,
           standardize=standardize,
           tracking_uri=tracking_uri)


def make_param_string(params):
    return (f"--pop-size={params['POP_SIZE']} "
            f"--epsilon-zero={params['E0']} "
            f"--beta={params['BETA']}")


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
@click.option("--tracking-uri", type=str, default="mlruns-ps")
def paramsearch(node, time, mem, tracking_uri):
    # Create experiments so we don't get races.
    mlflow.set_tracking_uri(tracking_uri)
    for module in xcsf_experiments:
        mlflow.set_experiment(experiment_name("xcsf", module))
        sleep(0.5)

    job_dir, results_dir = get_dirs()

    # TODO Can we get rid of the dependency on that module?
    from exp2022evostar.xcsf.parameter_search import param_grid

    for module in xcsf_experiments:
        sleep(5)
        for params in param_grid:
            submit(node,
                   time,
                   mem,
                   "xcsf",
                   module,
                   job_dir=job_dir,
                   results_dir=results_dir,
                   standardize=True,
                   tracking_uri=tracking_uri,
                   params=make_param_string(params),
                   n_reps=5)


main.add_command(paramsearch)
main.add_command(slurm)
main.add_command(slurm1)

if __name__ == "__main__":
    main()
