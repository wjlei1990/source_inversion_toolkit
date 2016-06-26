#!/usr/bin/env python
# ###########################################################
# Scripts that splits a large eventlist file into subfolders.
# For example, you have a eventlist contains 320 events.
# and you want to split it into 50 events/per file. There will
# be 6 files generated. The first 5 files will have 50 events
# while the last will have 20 events.
# The output job scripts will be put at "$runbase/jobs"
# ###########################################################

from __future__ import print_function, division
import os
import sys
import math
import yaml
from utils import copytree, cleantree, copyfile, get_permission
from utils import read_txt_into_list, dump_list_to_txt


def determine_nevents_per_job(config):
    mode = config[1]["running_mode"]
    print("Job running mode: %s" % mode)
    if mode == "simul_and_serial":
        nevents = \
            config[1]["nsimul_serial"] * config[1]["nevents_per_simul_run"]
    else:
        nevents = config[1]["nevents_per_simul_run"]
    return nevents


def print_split_summary(nevents_total, nevents_per_job, njobs):
    print("*"*20 + "\nSplit eventlist")
    print("Working mode:")
    print("Number of events:", nevents_total)
    print("Jobs per bundle:", nevents_per_job)
    print("Number of jobs:", njobs)


def check_eventlist(eventlist):
    if len(set(eventlist)) != len(eventlist):
        raise ValueError("There are duplicate elements in eventlist")


def split_eventlist(config):
    """
    Split the total event list to sub-job eventlist
    """

    nevents_per_job = determine_nevents_per_job(config)

    # read the input eventlist
    eventlist = read_txt_into_list(config[1]["total_eventfile"])
    nevents_total = len(eventlist)

    njobs = int(math.ceil(nevents_total/float(nevents_per_job)))

    num_total = 0
    eventlist_dict = {}
    for i in range(1, njobs+1):
        start_idx = (i-1) * nevents_per_job
        end_idx = min(i * nevents_per_job, nevents_total)
        print("job: %3d -- event index: [%4d --> %4d)" %
              (i, start_idx, end_idx))
        eventlist_dict[i] = eventlist[start_idx:end_idx]
        num_total += len(eventlist_dict[i])

    if num_total != nevents_total:
        raise ValueError("Event split Error!!! %d != %d"
                         % (num_total, nevents_total))

    print_split_summary(nevents_total, nevents_per_job, njobs)
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


def copy_cmtfiles(eventlist, cmtfolder, targetcmtdir):
    print("copy cmt:[%s --> %s]" % (cmtfolder, targetcmtdir))
    for _event in eventlist:
        origincmt = os.path.join(cmtfolder, _event)
        targetcmt = os.path.join(targetcmtdir, _event)
        copyfile(origincmt, targetcmt, verbose=False)


def copy_stations(eventlist, stafolder, targetstadir):
    print("copy stattion:[%s --> %s]" % (stafolder, targetstadir))
    for _event in eventlist:
        originsta = os.path.join(stafolder, "STATIONS.%s" % _event)
        targetsta = os.path.join(targetstadir, "STATIONS.%s" % _event)
        copyfile(originsta, targetsta, verbose=False)


def choose_template_folder(mode):
    mode = mode.lower()
    base = "job_running_template"
    if mode == "simul":
        dirname = os.path.join(base, "template_simul")
    elif mode == "simul_and_serial":
        dirname = os.path.join(base, "template_simul_and_serial")
    elif mode == "serial":
        dirname = os.path.join(base, "template_serial")
    else:
        raise ValueError("mode(%s) not recognized!")
    return dirname


def dump_eventlist_subdir(eventlist, targetdir):
        fn = os.path.join(targetdir, "_XEVENTID.all")
        dump_list_to_txt(fn, eventlist)


def copy_scripts_template(template_folder, targetdir):
    # copy scripts to generate deriv cmt files
    copytree("job_running_template/perturb_cmt",
             targetdir)

    # copy scripts template
    print("Copy scripts template:[%s --> %s]" %
          (template_folder, targetdir))
    copytree(template_folder, targetdir)


def create_job_folder(eventlist_dict, config):

    # create job folder
    tag = config[1]["job_tag"]
    cmtfolder = config[0]["cmtfolder"]
    stafolder = config[0]["stationfolder"]
    template_folder = choose_template_folder(config[1]["running_mode"])

    print("*"*20 + "\nCreat job sub folders")
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
        dump_eventlist_subdir(eventlist, targetdir)

        # copy original cmt file and station file
        targetcmtdir = os.path.join(targetdir, "cmtfile")
        copy_cmtfiles(eventlist, cmtfolder, targetcmtdir)

        targetstadir = os.path.join(targetdir, "station")
        copy_stations(eventlist, stafolder, targetstadir)

        # copy scripts template
        copy_scripts_template(template_folder, targetdir)

        # copy config.yaml file
        copyfile("config.yml", os.path.join(targetdir, "config.yml"))


def main():
    config_file = "config.yml"
    with open(config_file) as fh:
        config = list(yaml.load_all(fh))

    eventlist_dict = split_eventlist(config)

    # create job folder
    create_job_folder(eventlist_dict, config)


if __name__ == "__main__":
    main()
