import os
import pathlib
import shutil
import tempfile
from datetime import datetime
from subprocess import PIPE, Popen

seed0 = 0
data_seed0 = 0


def get_dirs():
    job_dir = os.getcwd()
    datetime_ = datetime.now().isoformat()
    results_dir = f"{job_dir}/results/{datetime_}"
    os.makedirs(f"{results_dir}/output", exist_ok=True)
    os.makedirs(f"{results_dir}/jobs", exist_ok=True)
    return job_dir, results_dir


def make_param_string(params):
    return (f"--pop-size={params['POP_SIZE']} "
            f"--epsilon-zero={params['E0']} "
            f"--beta={params['BETA']}")


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
        f'#SBATCH --partition=cpu-prio',
        f'#SBATCH --output="{results_dir}/output/output-%A-%a.txt"',
        f'#SBATCH --array=0-{njobs - 1}',
        (
            # provide job_dir to create the environment
            f'nix develop "{job_dir}" --command '
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
