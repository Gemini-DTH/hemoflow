import easyvvuq as uq
from dask.distributed import Client
import argparse
import os
import time
import numpy as np
import glob

# For hemoflow use the feature-aneurysm branch
TMP_DIR = os.environ.get("TMPDIR")
HEMOFLOW_PATH = os.environ.get("HEMOFLOW_PATH")

# For LBMpost use the dev branch
LBMPOST_PATH = os.environ.get("LBMPOST_PATH")
TEMPLATE_DIR_PATH = "campaign_dir"
TEMPLATE_DIR_PATH = os.path.abspath(TEMPLATE_DIR_PATH)

SAMPLE_CSV_PATH = "simulation_points_510_lin143_qmc.csv"
SAMPLE_CSV_PATH = os.path.abspath(SAMPLE_CSV_PATH)


def run_uncertainty_quantification(client_param):
    """
    Usage of EasyVVUQ for simulation verification study
    """
    work_dir = os.path.dirname(os.path.abspath(__file__))
    campaign = uq.Campaign(name="temp_uncertainty_test_", work_dir=work_dir)

    params = {
        "u": {"type": "string", "default": 0},  # you need to use string with CSV
        "l": {"type": "string", "default": 0},
        "q": {"type": "string", "default": 0},
    }

    encoder = uq.encoders.GenericEncoder(
        template_fname="{}/campaign_dir/input.template".format(work_dir),
        delimiter="$",
        target_filename="input.xml",
    )

    decoder = uq.decoders.SimpleCSV(
        target_filename="postProc/static_data.csv",
        output_columns=["ane_0_velocity_vol_avg"],
    )

    actions = uq.actions.Actions(
        uq.actions.CreateRunDirectory(root=work_dir, flatten=True),
        uq.actions.ExecuteLocal("cp --recursive " + TEMPLATE_DIR_PATH + "/. ./"),
        uq.actions.Encode(encoder),
        # Simulation
        # Number of processes for mpirun should be equal to the number of cores requested in SLURM job (job_cpu)
        uq.actions.ExecuteLocal("mpirun -n 12 " + HEMOFLOW_PATH + " input.xml"),
        # conda env for running LBMpost, livestream for stdio
        uq.actions.ExecuteLocal("conda run --live-stream -p $SCRATCH/post_env/lbmpost python3 -u {} ./ full -p".format(LBMPOST_PATH)),
        uq.actions.Decode(decoder),
    )

    campaign.add_app(name="hemoflow_uncertainty_", params=params, actions=actions)

    campaign.set_sampler(uq.sampling.CSVSampler(SAMPLE_CSV_PATH))

    try:
        campaign.execute(pool=client_param).collate()
        print("Simulation finished.")

        data_frame = campaign.get_collation_result()
        print(data_frame)
        data_frame.to_csv("uncertainty_output.csv")
    except Exception as e:
        print(f"ERROR: {e} – campaign state saved in campaign.db ...")



if __name__ == "__main__":

    """
    Parsing arguments to specify type of run. Possible options:
    --local - running locally.
    --slurm - running using SLURM with default option dask-jobqueue - deploy Dask
              on common job queuing systems on HPC.
    """
    parser = argparse.ArgumentParser(
        description="EasyVVUQ applied to a vertical tube deflection (using DASK).",
        epilog="",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--local", "-l", help="Run locally.", action="store_true", default=False
    )
    parser.add_argument(
        "--slurm",
        "-s",
        help="Run using SLURM. Possible options: dask-jobqueue",
        default="dask-jobqueue",
    )

    args = parser.parse_args()

    """
    Creating client from dask.distributed according chosen run type.
    """
    if args.local:
        print("Running locally")
        client = Client(processes=True, n_workers=1, threads_per_worker=1)
        run_uncertainty_quantification(client)
    elif args.slurm == "dask-jobqueue":
        print("Running with SLURM using dask-jobqueue.")
        from dask_jobqueue import SLURMCluster

        job_script_prologue = [
            "module load hdf5",
            "module load cmake",
            "cd $TMPDIR",
            "mkdir env_mountpoint",
            "squashfuse $SCRATCH/lbmpost/LBMenv.squashfs env_mountpoint",
            "conda activate $TMPDIR/env_mountpoint",
        ]

        # Cluster allocation should be adapted to the needs of the campaign 
        cluster = SLURMCluster(
            shebang="#!/bin/bash -l",
            queue="plgrid",
            account="plggemini2026-cpu",
            cores=1,
            processes=1,
            memory="48GB",
            walltime="32:00:00",
            interface="ib0",
            scheduler_options={"interface": "ib0"},
            python="python3",
            n_workers=1,
            job_cpu=12,
            job_script_prologue=job_script_prologue,
            worker_extra_args=["--memory-limit 1GiB","--lifetime", "32h", "--lifetime-stagger", "4m"],
            job_extra_directives=[
                "--output ./slurm-%j.out",
                "--error ./slurm-%j.err",
            ],
        )

        cluster.job_cls.submit_command = "sbatch"
        cluster.submit_command = "sbatch"
        cluster.adapt(minimum=int(os.environ.get("JOBS_NUM_MIN")), maximum=int(os.environ.get("JOBS_NUM_MAX")))
        client = Client(cluster)
        client.run(lambda dask_worker: setattr(dask_worker, "retries", 2))
        print(cluster)
        print(client)
        
        from dask.distributed import performance_report

        with performance_report(filename="dask-report.html"):
            run_uncertainty_quantification(client)

    else:
        print("Incorrect slurm option specified!")
        exit(1)