#!/usr/bin/env python
import glob
import os
from utils import cleantree

from copy_files import copy_files
from create_job_pbs import create_job_pbs
import yaml
from perturb_cmt import gen_cmt_wrapper


def perturb_cmt(cmtdir, dmoment_tensor, dlatitude, dlongitude, ddepth):
    
    with open("XEVENTID") as fh:
        content = fh.readlines()
    eventlist = [x.rstrip("\n") for x in content]

    for event in eventlist:
        cmtfile = os.path.join(cmtdir, event)
        print("Peturb CMT file: %s" % cmtfile)
        if not os.path.exists(cmtfile):
            raise ValueError("cmtfile not exists: %s" % cmtfile)
        gen_cmt_wrapper(cmtfile, dmoment_tensor=dmoment_tensor,
                        dlongitude=dlongitude, dlatitude=dlatitude,
                        ddepth=ddepth, output_dir=cmtdir)


def prepare_dir():
    with open("./config.yaml") as fh:                                          
        config = yaml.load(fh)                                                  

    # copy specfem stuff
    copy_files()

    # perturb cmt files
    generate_deriv_cmt = config["generate_deriv_cmt"]
    if generate_deriv_cmt:
        cmtdir = "cmtfile"
        dmoment_tensor = config["dmoment_tensor"]
        ddepth = config["ddepth"]
        dlatitude = config["dlatitude"]
        dlongitude = config["dlongitude"]
        perturb_cmt(cmtdir, dmoment_tensor, dlatitude, dlongitude, ddepth)

    # create job pbs files
    nevents_per_job = config["nevents_per_job"]                                 
    walltime_per_simulation = config["walltime_per_simulation"] 
    deriv_cmt_list = config["deriv_cmt_list"]
    create_job_pbs(nevents_per_job, walltime_per_simulation, deriv_cmt_list)

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
