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
from utils import safe_makedir, copyfile
from utils import read_txt_into_list, dump_list_to_txt


def perturb_cmt(eventlist, cmtdir, config):

    dmoment_tensor = config["dmoment_tensor"]
    ddepth = config["ddepth"]
    dlatitude = config["dlatitude"]
    dlongitude = config["dlongitude"]

    for idx, event in enumerate(eventlist):
        cmtfile = os.path.join(cmtdir, event)
        print("%03d Peturb CMT file: %s" % (idx, cmtfile))
        if not os.path.exists(cmtfile):
            raise ValueError("cmtfile not exists: %s" % cmtfile)
        gen_cmt_wrapper(cmtfile, dmoment_tensor=dmoment_tensor,
                        dlongitude=dlongitude, dlatitude=dlatitude,
                        ddepth=ddepth, output_dir=cmtdir)


def setup_simul_run_dir(runbase, nruns):
    # copy specfem related files to sub directory
    specfemdir = os.path.join(runbase, "specfem3d_globe")

    # clean previous run_**** first
    dirlist = glob.glob(os.path.join(specfemdir, "run*"))
    print("remove dirlist: ", dirlist)
    for _dir in dirlist:
        shutil.rmtree(_dir)

    # make run**** dir and DATABASES_MPI
    for i in range(nruns):
        job_idx = i + 1
        sub_dir = os.path.join(specfemdir, "run%04d" % job_idx)
        print("Working on job running sub-dir: %s" % sub_dir)
        safe_makedir(sub_dir)
        if job_idx == 1:
            dir1 = os.path.join(sub_dir, "DATABASES_MPI")
            dir2 = os.path.join(specfemdir, "DATABASES_MPI")
            os.symlink(dir2, dir1)
        else:
            safe_makedir(os.path.join(sub_dir, "DATABASES_MPI"))


def setup_outputbase(config, eventlist):
    """
    Make directory at ./outputbase for each event. Create DATA and
    OUTPUT_FILES directories and copy necessary files, including
    CMTSOLUTION, STATIONS, values_from_mesher.h and addressing.txt
    """
    filelist = ["values_from_mesher.h", "addressing.txt"]

    outputbase = "outputbase"
    derivs = config[2]["deriv_cmt_list"]
    specfemdir = os.path.join(config[1]["runbase"], "specfem3d_globe")

    suffixs = ["_%s" % deriv for deriv in derivs]
    suffixs.append("")
    print("set up output base at: %s" % outputbase)
    print("suffixs: %s" % suffixs)
    for idx, event in enumerate(eventlist):
        print("%03d event: %s" % (idx, event))
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


def split_eventlist(eventlist, nsimuls, nserials):
    nevents_total = len(eventlist)
    if nevents_total > nsimuls * nserials or \
            nevents_total < nsimuls * (nserials - 1):
        raise ValueError("Length of eventlist(%d) is in range of "
                         "nsimul_runs(%d) and nsimul_serial(%d)"
                         % (nevents_total, nsimuls, nserials))

    for i in range(nserials):
        idx_start = nsimuls * i
        idx_end = min(nsimuls * (i+1), nevents_total)
        sub_events = eventlist[idx_start:idx_end]
        job_id = i + 1
        fn = "XEVENTID.%d" % job_id
        dump_list_to_txt(fn, sub_events)

    print("Number of events total: %d" % nevents_total)
    print("Number of serial simul runs: %d" % nserials)
    print("Number of events in an simul run: %d" % nsimuls)


def prepare_dir(config, eventlist):

    # copy specfem stuff
    print("-" * 10 + "  setup simul run sub-dir  " + "-" * 10)
    setup_simul_run_dir(config[1]["runbase"],
                        config[1]["nevents_per_simul_run"])

    # split the whole eventlist into sub eventlist according to
    # config[1]["nevents_per_simul_runs"]
    split_eventlist(eventlist, config[1]["nevents_per_simul_run"],
                    config[1]["nsimul_serial"])

    # perturb cmt files
    print("-" * 10 + "  perturb cmtsolutions  " + "-" * 10)
    cmtdir = "cmtfile"
    perturb_cmt(eventlist, cmtdir, config[2])

    # setup output base
    print("-"*10 + "  setup output base  " + "-" * 10)
    setup_outputbase(config, eventlist)

    # setup job scripts
    print("-"*10 + "  setup job scripts  " + "-" * 10)
    setup_job_scripts(config, eventlist)

    print("*"*30)
    print("Please check related files and then submit jobs")
    print("Use: ./submit.bash")
    print("*"*30)


if __name__ == "__main__":
    with open("./config.yml") as fh:
        config = list(yaml.load_all(fh))
    eventlist = read_txt_into_list("_XEVENTID.all")

    prepare_dir(config, eventlist)
