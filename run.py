import os
import pathlib
import shutil
import tempfile
from subprocess import PIPE, Popen
from time import sleep

import click
import mlflow
from experiments import experiment_name
from experiments.berbl import BERBLExperiment
from experiments.xcsf import XCSFExperiment
from exp2022evostar.xcsf.parameter_search import param_grid


@click.command()
@click.argument("ALGORITHM")
@click.argument("MODULE")
@click.option("-n", "--n-iter", type=click.IntRange(min=1))
@click.option("-s",
              "--seed",
              type=click.IntRange(min=0),
              default=0,
              show_default=True)
@click.option("--data-seed",
              type=click.IntRange(min=0),
              default=1,
              show_default=True)
@click.option("--show/--no-show", type=bool, default=False, show_default=True)
@click.option("--standardize/--no-standardize",
              type=bool,
              default=False,
              show_default=True)
# only applicable to berbl
@click.option("--fit-mix", type=str, default=None)
@click.option("--literal/--no-literal", type=bool, default=None)
@click.option("--match", type=str, default=None)
# only applicable to XCSF
@click.option("-p", "--pop-size", type=click.IntRange(min=1), default=100)
@click.option("--epsilon-zero", type=float, default=0.01)
@click.option("--beta", type=float, default=0.01)
@click.option("--run-name", type=str, default=None)
@click.option("--tracking-uri", type=str, default="mlruns")
def main(algorithm, module, n_iter, seed, data_seed, show, standardize,
         fit_mix, literal, match, pop_size, epsilon_zero, beta, run_name,
         tracking_uri):
    """
    Use ALGORITHM ("berbl" or "xcsf") in an experiment defined by MODULE
    (module path appended to "experiments.ALGORITHM.").
    """
    algorithms = ["berbl", "xcsf"]
    if not algorithm in algorithms:
        print(f"ALGORITHM has to be one of {algorithms} but is {algorithm}")
        exit(1)

    if algorithm == "berbl":
        exp = BERBLExperiment(module,
                              seed=seed,
                              data_seed=data_seed,
                              standardize=standardize,
                              show=show,
                              run_name=run_name,
                              tracking_uri=tracking_uri,
                              exp_path_prefix="exp2022evostar")
        exp.run(n_iter=n_iter,
                match=match,
                literal=literal,
                fit_mixing=fit_mix)
    elif algorithm == "xcsf":
        exp = XCSFExperiment(module,
                             seed=seed,
                             data_seed=data_seed,
                             standardize=standardize,
                             show=show,
                             run_name=run_name,
                             tracking_uri=tracking_uri,
                             exp_path_prefix="exp2022evostar")
        exp.run(MAX_TRIALS=n_iter,
                POP_SIZE=pop_size,
                E0=epsilon_zero,
                BETA=beta)
    else:
        print(f"Algorithm {algorithm} not one of [berbl, xcsf].")


if __name__ == "__main__":
    main()

# Local Variables:
# mode: python
# End:
