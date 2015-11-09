#!/usr/bin/env python
import glob
from utils import cleantree

from copy_files import copy_files
from create_job_pbs import create_job_pbs
import yaml


def perturb_cmt():
    pass


def prepare_dir():
    with open("../config.yaml") as fh:                                          
        config = yaml.load(fh)                                                  
    # copy specfem stuff
    copy_files()

    # perturb cmt files
    perturb_cmt()

    # create job pbs files
    nevents_per_job = config["nevents_per_job"]                                 
    nnodes_per_simulation = config["nnodes_per_simulation"]                     
    walltime_per_simulation = config["walltime_per_simulation"] 
    create_job_pbs(nevents_per_job, nnodes_per_simulation,
                   walltime_per_simulation)

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
