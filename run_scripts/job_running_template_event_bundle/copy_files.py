#!/usr/bin/env python
import os
import glob
import shutil

def check_exist(filename):
    if not os.path.exists(filename):
        raise ValueError("Path not exists: %s" % filename)


def read_txt_into_list(filename):
    with open(filename, "r") as f:
        content = f.readlines()
    return [x.rstrip("\n") for x in content]


def copy_cmtfile(cmtfile, targetdir):
    destdir = os.path.join(targetdir, "DATA/CMTSOLUTION")
    shutil.copy2(cmtfile, destdir)
        

def copy_derivative_cmtfile(cmtfile_prefix, destdir):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    exts=("", "_Mrr", "_Mtt", "_Mpp", "_Mrt", "_Mrp", "_Mtp", 
          "_dep", "_lat", "_lon")
    for _ext in exts:
        cmtfile = cmtfile_prefix + _ext
        shutil.copy2(cmtfile, destdir)


def cleantree(folder):
    if not os.path.exists(folder):
        return
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): 
                #shutil.rmtree(file_path)
        except Exception, e:
            print e


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(src):
        raise ValueError("Src dir not exists: %s" % src)
    if not os.path.exists(dst):
        raise ValueError("Dest dir not exists: %s" % dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


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
    if len(meshfiles) <= 5:
        raise ValueError("No enough mesh files. Double check:%s" % targetdir)


if __name__ == "__main__":

    scratch_dir="../.."
    eventfile="XEVENTID"
    cmtcenter="/ccs/home/lei/SOURCE_INVERSION/CMT_BIN/ALL_CMT"
    specfemdir = os.path.join(scratch_dir, "specfem_stuff")
    datacenter = os.path.join(scratch_dir, "DATA")

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
        copy_derivative_cmtfile(cmtfile, "cmtfile")
        
        check_mesh(targetdir)

