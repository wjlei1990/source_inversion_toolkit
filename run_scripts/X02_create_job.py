#!/usr/bin/env python
# ###########################################################
# Scripts that splits a large eventlist file. 
# For example, you have a eventlist contains 320 events.
# and you want to split it into 50 events/per file. There will
# be 6 files generated. The first 5 files will have 50 events
# while the last will have 20 events.
# ###########################################################

import os
import glob
import math
import sys
import shutil
import yaml
from utils import copytree, cleantree, copyfile
from utils import read_txt_into_list


def split_eventlist(inputfile, njobs_bundle, outputdir, output_base):

    # clean up the outputdir
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    temp_list = glob.glob(os.path.join(outputdir, "*"))
    for _file in temp_list:
        os.remove(_file)

    # read the input eventlist
    with open(inputfile, 'r') as f:
        content = f.readlines()
    eventlist = [ line.rstrip('\n') for line in content ]

    nevents = len(eventlist)
    njobs = int(math.ceil(nevents/float(njobs_bundle)))
 
    print("*"*20 + "\nSplit eventlist")
    print "Number of events:", nevents
    print "Jobs per bundle:", njobs_bundle
    print "Number of jobs:", njobs

    eventlist_dict = {}
    for i in range(1, njobs+1):
        start_index = (i-1) * njobs_bundle
        end_index = min( i*njobs_bundle, nevents )
        outputfn = os.path.join(outputdir, "%s%d" %(output_base, i))
        print("job: %3d -- event index: [%4d --> %4d) -- output: %s" % 
                (i, start_index, end_index, outputfn))
        with open(outputfn, 'w') as f:
            for _ind in range(start_index, end_index):
                f.write("%s\n" % eventlist[_ind])
        eventlist_dict[i] = outputfn
    
    return eventlist_dict


def check_job_folder_exist(targetdir_list):
    clean_status = 1
    for targetdir in targetdir_list:
        if os.path.exists(targetdir):
            print("job folder exists: %s" % targetdir)
            clean_status = 0

    if clean_status == 0:
        answer = raw_input("Remove[Y/n]:")
        if answer == "Y":
            print("Removing all...")
            for _dir in targetdir_list:
                if not os.path.exists(_dir):
                    os.makedirs(_dir)
                else:
                    cleantree(_dir)
        elif anser == "n":
            raise ValueError("Quit as requested") 
        else:
            raise ValueError("Incorrect input")
 

def copy_cmtfiles(_event, cmtfolder, targetcmtdir, generate_deriv_cmt,
                  deriv_cmt_list):
    origincmt = os.path.join(cmtfolder, _event)
    targetcmt = os.path.join(targetcmtdir, _event)
    copyfile(origincmt, targetcmt, verbose=False)
    if not generate_deriv_cmt:
        # copy deriv cmt files
        for deriv_type in deriv_cmt_list:
            derivcmt = os.path.join(cmtfolder, "%s_%s" % (_event, deriv_type)) 
            targetcmt = os.path.join(targetcmtdir, "%s_%s" 
                                     % (_event, deriv_type))
            copyfile(derivcmt, targetcmt, verbose=False)
    else:
        # copy scripts to generate deriv cmt files
        copytree("job_running_template/perturb_cmt", 
                 os.path.dirname(targetcmtdir))


def copy_stations(_event, stationfolder, targetstadir):
    originsta = os.path.join(stationfolder, "%s.STATIONS" % _event)
    targetsta = os.path.join(targetstadir, "%s.STATIONS" % _event)
    copyfile(originsta, targetsta, verbose=False)


def create_job_folder(template_folder, tag, eventlist_dict, cmtfolder,
                      stafolder, generate_deriv_cmt, deriv_cmt_list):

    targetdir_list = []
    print("*"*20 + "\nCreat job sub folder")
    for _i in range(len(eventlist_dict)):
        idx = _i + 1
        targetdir = "job_" + tag + "_%02d" % idx
        targetdir_list.append(targetdir)

    check_job_folder_exist(targetdir_list)

    for _i, targetdir in enumerate(targetdir_list):
        idx = _i + 1
        print("="*5 + "\nJob id: %d" % idx)
        # copy eventlist file
        eventlist_file = eventlist_dict[idx]
        targetfile = os.path.join(targetdir, "XEVENTID")
        copyfile(eventlist_file, targetfile)

        # copy original cmt file and station file
        targetcmtdir = os.path.join(targetdir, "cmtfile")
        targetstadir = os.path.join(targetdir, "station")
        print("copy cmt:[%s --> %s]" % (cmtfolder, targetcmtdir))
        print("copy stattion:[%s --> %s]" % (stafolder, targetstadir))
        events = read_txt_into_list(eventlist_file)
        for _event in events:
            copy_cmtfiles(_event, cmtfolder, targetcmtdir, generate_deriv_cmt,
                          deriv_cmt_list)
            copy_stations(_event, stafolder, targetstadir)


        print("Copy dir:[%s --> %s]" % (template_folder, targetdir))
        # copy scripts template
        copytree(template_folder, targetdir)

        # copy config.yaml file
        copyfile("config.yaml", os.path.join(targetdir, "config.yaml"))


if __name__ == "__main__":
    config_file = "config.yaml"
    with open(config_file) as fh:
        config = yaml.load(fh)

    eventlist_dir = "_event_split_list_"
    eventlist_base = "EVENTID_LIST_"
    runbase_size = config["runbase_size"]

    # split event list
    eventfile = config["total_eventfile"]
    eventlist_dict = split_eventlist(eventfile, runbase_size, eventlist_dir, 
                                     eventlist_base)

    # create job folder
    tag = config["job_tag"]
    running_mode = config["running_mode"]
    cmtfolder = config["cmtfolder"]
    stafolder = config["stationfolder"]
    generate_deriv_cmt = config["generate_deriv_cmt"]
    deriv_cmt_list = config["deriv_cmt_list"]
    if running_mode == "bundle":
        template_folder = "./job_running_template/template_bundle"
    elif running_mode == "single":
        template_folder = "./job_running_template/template_single"

    create_job_folder(template_folder, tag, eventlist_dict, cmtfolder,
                      stafolder, generate_deriv_cmt, deriv_cmt_list)

