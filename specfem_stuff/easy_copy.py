#!/usr/bin/env python
# ##########################
# easy copy all necessary files of specfem3d_globe into
# target directory
import os
import glob
import shutil


def safe_copy(fn, specfemdir, targetdir):
    origin_file = os.path.join(specfemdir, fn)
    target_file = os.path.join(targetdir, fn)
    if not os.path.exists(origin_file):
        raise ValueError("No such file: %s" % fn)

    if not os.path.exists(os.path.dirname(target_file)):
        os.makedirs(os.path.dirname(target_file))

    print("Copy files:[%s --> %s]" % (origin_file, target_file))
    shutil.copy2(origin_file, target_file)


def safe_copy_model_file(specfemdir, targetdir):
    origindir = os.path.join(specfemdir, "DATABASES_MPI")
    model_files = glob.glob(os.path.join(origindir, "*"))

    if len(model_files) == 0:
        raise ValueError("No model files at dir: %s" % origindir)

    target_model_dir = os.path.join(targetdir, "DATABASES_MPI")
    if not os.path.exists(target_model_dir):
        os.makedirs(target_model_dir)

    for _file in model_files:
        print("Copy files:[%s --> %s]" % (_file, target_model_dir))
        shutil.copy2(_file, target_model_dir)


def quick_check(specfemdir, filelist):
    for _file in filelist:
        path = os.path.join(specfemdir, _file)
        if not os.path.exists(path):
            raise ValueError("File not exists: %s" % (path))

    # check model file
    path = os.path.join(specfemdir, "DATABASES_MPI")
    bpfiles = glob.glob(os.path.join(path, "*.bp"))
    binfiles = glob.glob(os.path.join(path, "*.bin"))
    if len(bpfiles) == 4:
        if len(binfiles) != 1:
            raise ValueError("Check model files: %s" % path)
    elif len(bpfiles) == 0:
        if len(binfiles) <= 2:
            raise ValueError("Check model files: %s" % path)
    else:
        raise ValueError("Check model files: %s" % path)


if __name__ == "__main__":

    print("******************************************")
    print("Please specify the directory of specfem")
    specfemdir = raw_input("specfemdir=")

    targetdir = "."

    if not os.path.exists(specfemdir):
        raise ValueError("No specfem dir: %s" % specfemdir)

    filelist = ["bin/xspecfem3D", "OUTPUT_FILES/addressing.txt",
                "OUTPUT_FILES/values_from_mesher.h", "DATA/STATIONS",
                "DATA/Par_file"]

    quick_check(specfemdir, filelist)

    print("--------------------------")
    print("Copy from dir: %s" % specfemdir)
    for fn in filelist:
        safe_copy(fn, specfemdir, targetdir)

    safe_copy_model_file(specfemdir, targetdir)
