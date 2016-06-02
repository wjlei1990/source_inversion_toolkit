#!/usr/bin/env python
# #####################################################################
# Scripts that prepare files for the job submission
# 1) setup_simul_run: mkdir "$runbase/specfem3d_globe/run_00XX" directories
#       for the simulatenous run and DATABASES_MPI.
# 2) perturb_cmt: perturb cmt based on values in config.yml.
# 3) setup_outputbase: mkdir './outputbase' and prepare "DATA/" and
#       "OUTPUT_FILES" for each event. Then at the running stage,
#       these two directories will be symlinked to "run_00XX"
# 4) setup_job_scripts: modify job scripts so they are ready for job
#       submission
# #####################################################################
from __future__ import print_function, division
import glob
import os
import yaml
import shutil

from create_job_pbs import setup_job_scripts
from perturb_cmt import gen_cmt_wrapper
from utils import safe_makedir, copyfile, read_txt_into_list


def perturb_cmt(cmtdir, config):

    dmoment_tensor = config["dmoment_tensor"]
    ddepth = config["ddepth"]
    dlatitude = config["dlatitude"]
    dlongitude = config["dlongitude"]

    eventlist = read_txt_into_list("XEVENTID")

    for event in eventlist:
        cmtfile = os.path.join(cmtdir, event)
        print("Peturb CMT file: %s" % cmtfile)
        if not os.path.exists(cmtfile):
            raise ValueError("cmtfile not exists: %s" % cmtfile)
        gen_cmt_wrapper(cmtfile, dmoment_tensor=dmoment_tensor,
                        dlongitude=dlongitude, dlatitude=dlatitude,
                        ddepth=ddepth, output_dir=cmtdir)


def setup_simul_run(runbase, nruns):
    # copy specfem related files to sub directory
    specfemdir = os.path.join(runbase, "specfem3d_globe")

    # clean previous run_**** first
    dirlist = glob.glob(os.path.join(specfemdir, "run_*"))
    print("remove dirlist: ", dirlist)
    for _dir in dirlist:
        shutil.rmtree(_dir)

    for i in range(nruns):
        job_idx = i + 1
        sub_dir = os.path.join(specfemdir, "run_%04d" % job_idx)
        print("Working on job running sub-dir: %s" % sub_dir)
        safe_makedir(sub_dir)
        if job_idx == 1:
            dir1 = os.path.join(sub_dir, "DATABASES_MPI")
            dir2 = os.path.join(specfemdir, "DATABASES_MPI")
            os.symlink(dir2, dir1)
        else:
            safe_makedir(os.path.join(sub_dir, "DATABASES_MPI"))


def setup_outputbase(config):
    filelist = ["values_from_mesher.h", "addressing.txt"]

    outputbase = "outputbase"
    eventlist = read_txt_into_list("XEVENTID")
    derivs = config[2]["deriv_cmt_list"]
    specfemdir = os.path.join(config[1]["runbase"], "specfem3d_globe")

    suffixs = ["_%s" % deriv for deriv in derivs]
    suffixs.append("")
    print("set up output base at: %s" % outputbase)
    print("suffixs: %s" % suffixs)
    for event in eventlist:
        print("event: " + event)
        for deriv in suffixs:
            _dir = os.path.join(outputbase, "%s%s" % (event, deriv))
            safe_makedir(_dir)
            safe_makedir(os.path.join(_dir, "DATA"))
            safe_makedir(os.path.join(_dir, "OUTPUT_FILES"))
            # copy stations, cmtfile into outputbase
            cmtfile1 = os.path.join("cmtfile", "%s%s" % (event, deriv))
            cmtfile2 = os.path.join(_dir, "DATA", "CMTSOLUTION")
            copyfile(cmtfile1, cmtfile2, verbose=False)

            stafile1 = os.path.join("station", "STATIONS.%s" % event)
            stafile2 = os.path.join(_dir, "DATA", "STATIONS")
            copyfile(stafile1, stafile2, verbose=False)

            # for DATA, OUTPUT_FILES and SEM, we only create symbolic link
            for _file in filelist:
                file1 = os.path.join(specfemdir, "OUTPUT_FILES", _file)
                file2 = os.path.join(_dir, "OUTPUT_FILES", _file)
                copyfile(file1, file2, verbose=False)


def prepare_dir(config):

    # copy specfem stuff
    print("-" * 10 + "  setup simul run sub-dir  " + "-" * 10)
    setup_simul_run(config[1]["runbase"], config[1]["nevents_per_mpirun"])

    # perturb cmt files
    print("-" * 10 + "  perturb cmtsolutions  " + "-" * 10)
    cmtdir = "cmtfile"
    perturb_cmt(cmtdir, config[2])

    # setup output base
    print("-"*10 + "  setup output base  " + "-" * 10)
    setup_outputbase(config)

    # setup job scripts
    print("-"*10 + "  setup job scripts  " + "-" * 10)
    setup_job_scripts(config)

    print("*"*30)
    print("Please check related files and then submit jobs")
    print("Use: ./submit.bash")
    print("*"*30)


if __name__ == "__main__":
    with open("./config.yml") as fh:
        config = list(yaml.load_all(fh))
    prepare_dir(config)
