# BERBL experiments for the 2022 GECCO paper


Code for repeating the experiments that were conducted for [this
paper](https://doi.org/10.1145/3512290.3528736).


## How to run the experiments


1. Install
   [Nix](https://nixos.org/manual/nix/stable/installation/installing-binary.html)
   [including flakes support](https://nixos.wiki/wiki/Flakes) in order to be
   able to run `nix develop` later.  Note that [Nix does not yet support
   Windows](https://nixos.org/manual/nix/stable/installation/supported-platforms.html).
2. Clone the repository (`git clone …`). Run the next steps from within the
   cloned repository.
3. Enter a shell that contains all dependencies by running
   ```bash
   nix develop
   ```
   (may take some time to complete).
4. Run XCSF parameter study experiments, results are stored in a subfolder of
   `results`.
   ```bash
   PYTHONPATH=src:$PYTHONPATH python submit.py paramsearch HOST
   ```

   Note: *This currently requires Slurm* (see `submit.py`) a basic setup of
   which is rather simple to set up on a single machine. You could also get
   around using Slurm at all by writing custom `srun`/`sbatch` scripts that do
   not perform calls to  Slurm but simply run their argument (however, be aware
   that *a lot of processes may be spawned at once that way* if this is done too
   naively).

5. Optional: Enter parameter settings recommended by parameter study in
   experiment configurations under `src/experiments/xcsf/book/`.
6. Run the remaining experiments (requires Slurm as well, but see note regarding
   4.).
   ```bash
   PYTHONPATH=src:$PYTHONPATH python submit.py slurm HOST
   ```
7. In order to analyse the results, see [the berbl-eval-2022-gecco
   repository](https://github.com/berbl-dev/berbl-eval-2022-gecco).


<!-- Local Variables: -->
<!-- mode: markdown -->
<!-- End: -->
