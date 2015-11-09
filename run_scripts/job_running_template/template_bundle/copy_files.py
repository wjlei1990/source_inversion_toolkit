#!/usr/bin/env python
import os
import glob
import shutil
from utils import cleantree, copytree, copyfile, read_txt_into_list
from utils import check_exist


def copy_cmtfile(cmtfile, targetdir):
    destfile = os.path.join(targetdir, "DATA/CMTSOLUTION")
    copyfile(cmtfile, destfile)
        

def copy_derivative_cmtfile(cmtfile_prefix, destdir):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    exts=("", "_Mrr", "_Mtt", "_Mpp", "_Mrt", "_Mrp", "_Mtp", 
          "_dep", "_lat", "_lon")
    for _ext in exts:
        cmtfile = cmtfile_prefix + _ext
        destcmt = os.path.join(destdir, os.path.basename(cmtfile))
        copyfile(cmtfile, destcmt)


def copy_specfem_stuff(specfemdir, targetdir):
    dir_list = ["DATA", "OUTPUT_FILES", "bin"]
    # copy DATA
    for _dir in dir_list:
        fromdir = os.path.join(specfemdir, _dir)
        todir = os.path.join(targetdir, _dir)
        cleantree(todir)
        copytree(fromdir, todir)


def check_mesh(targetdir):
    meshdir = os.path.join(targetdir, "DATABASES_MPI")
    
    meshfiles = glob.glob(os.path.join(meshdir, "*"))
    if len(meshfiles) < 5:
        raise ValueError("No enough mesh files. Double check:%s" % targetdir)


def copy_files():

    cmtcenter="cmtfile"
    eventfile="XEVENTID"
    scratch_dir="../.."
    specfemdir = os.path.join(scratch_dir, "specfem_stuff")
    datacenter = os.path.join(scratch_dir, "RUN_BASE")

    check_exist(eventfile)
    check_exist(cmtcenter)
    check_exist(specfemdir)
    check_exist(datacenter)

    eventlist = read_txt_into_list(eventfile)
    print("Number of events: %d" % len(eventlist))

    for _idx, event in enumerate(eventlist):
        idx = _idx + 1
        cmtfile = os.path.join(cmtcenter, event)
        targetdir = os.path.join(datacenter, "event_%03d" % idx)
        check_exist(cmtfile)
        check_exist(targetdir)
        print("*"*20)
        print("event: %s" % event)
        print("cmtfile: %s" % cmtfile)
        print("targetdir: %s" % targetdir)

        copy_specfem_stuff(specfemdir, targetdir)
        copy_cmtfile(cmtfile, targetdir)
        #copy_derivative_cmtfile(cmtfile, "cmtfile")
        
        check_mesh(targetdir)


if __name__ == "__main__":
    copy_files()
