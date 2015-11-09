#!/usr/bin/env python
import glob
from utils import cleantree

from copy_files import copy_files
from create_job_pbs import create_job_pbs


def prepare_dir():
    # copy specfem stuff
    copy_files()
    # perturb cmt files
    perturb_cmt()
    # create job pbs files
    create_job_pbs()

    njobs = len(glob.glob("job_solver_bundle.pbs.*"))
    if njobs < 1:
        raise ValueError("No job scripts")

    # clean up temp data archive
    cleantree("data")

    print("*"*30)
    print("Please check related files and then submit jobs")
    print("Use: ./submit.bash")
    print("*"*30)


if __name__ == "__main__":
    prepare_dir()
