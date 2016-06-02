#!/usr/bin/env python
# ###########################################################
# Scripts that splits a large eventlist file into subfolders.
# For example, you have a eventlist contains 320 events.
# and you want to split it into 50 events/per file. There will
# be 6 files generated. The first 5 files will have 50 events
# while the last will have 20 events.
# The output job scripts will be put at "runbase/jobs"
# ###########################################################

import os
import sys
import math
import yaml
from utils import copytree, cleantree, copyfile, get_permission
from utils import read_txt_into_list, dump_list_to_txt


def split_eventlist(eventlist_file, nevents_mpi):

    # read the input eventlist
    eventlist = read_txt_into_list(eventlist_file)

    nevents = len(eventlist)
    njobs = int(math.ceil(nevents/float(nevents_mpi)))

    print("*"*20 + "\nSplit eventlist")
    print "Number of events:", nevents
    print "Jobs per bundle:", nevents_mpi
    print "Number of jobs:", njobs

    num_total = 0
    eventlist_dict = {}
    for i in range(1, njobs+1):
        start_idx = (i-1) * nevents_mpi
        end_idx = min(i * nevents_mpi, nevents)
        print("job: %3d -- event index: [%4d --> %4d)" %
              (i, start_idx, end_idx))
        eventlist_dict[i] = eventlist[start_idx:end_idx]
        num_total += len(eventlist_dict[i])

    if num_total != nevents:
        raise ValueError("Event split Error!!! %d != %d"
                         % (num_total, nevents))

    return eventlist_dict


def check_job_folder_exist(targetdir_list):
    clean_status = 1
    for targetdir in targetdir_list:
        if os.path.exists(targetdir):
            print("job folder exists: %s" % targetdir)
            clean_status = 0

    if clean_status == 0:
        print("Removed?")
        if get_permission():
            for _dir in targetdir_list:
                if os.path.exists(_dir):
                    cleantree(_dir)
        else:
            sys.exit(0)


def copy_cmtfiles(_event, cmtfolder, targetcmtdir):
    origincmt = os.path.join(cmtfolder, _event)
    targetcmt = os.path.join(targetcmtdir, _event)
    copyfile(origincmt, targetcmt, verbose=False)

    # copy scripts to generate deriv cmt files
    copytree("job_running_template/perturb_cmt",
             os.path.dirname(targetcmtdir))


def copy_stations(_event, stationfolder, targetstadir):
    originsta = os.path.join(stationfolder, "STATIONS.%s" % _event)
    targetsta = os.path.join(targetstadir, "STATIONS.%s" % _event)

    copyfile(originsta, targetsta, verbose=False)


def create_job_folder(eventlist_dict, config):

    # create job folder
    tag = config[1]["job_tag"]
    cmtfolder = config[0]["cmtfolder"]
    stafolder = config[0]["stationfolder"]
    template_folder = "./job_running_template/template_simul"

    print("*"*20 + "\nCreat job sub folder")
    jobs_dir = os.path.join(config[1]["runbase"], "jobs")
    targetdirs = [os.path.join(jobs_dir, "job_%s_%02d" % (tag, idx))
                  for idx in eventlist_dict]
    check_job_folder_exist(targetdirs)

    for _idx, targetdir in enumerate(targetdirs):
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)

        job_idx = _idx + 1
        print("="*5 + "\nJob id: %d" % job_idx)

        eventlist = eventlist_dict[job_idx]
        fn = os.path.join(targetdir, "XEVENTID")
        dump_list_to_txt(fn, eventlist)

        # copy original cmt file and station file
        targetcmtdir = os.path.join(targetdir, "cmtfile")
        targetstadir = os.path.join(targetdir, "station")
        print("copy cmt:[%s --> %s]" % (cmtfolder, targetcmtdir))
        print("copy stattion:[%s --> %s]" % (stafolder, targetstadir))
        for _event in eventlist:
            copy_cmtfiles(_event, cmtfolder, targetcmtdir)
            copy_stations(_event, stafolder, targetstadir)

        print("Copy scripts template:[%s --> %s]" %
              (template_folder, targetdir))
        # copy scripts template
        copytree(template_folder, targetdir)

        # copy config.yaml file
        copyfile("config.yml", os.path.join(targetdir, "config.yml"))


if __name__ == "__main__":

    config_file = "config.yml"
    with open(config_file) as fh:
        config = list(yaml.load_all(fh))

    # split total event list
    eventfile = config[1]["total_eventfile"]
    nevents_per_mpirun = config[1]["nevents_per_mpirun"]
    eventlist_dict = split_eventlist(eventfile, nevents_per_mpirun)

    # create job folder
    create_job_folder(eventlist_dict, config)
