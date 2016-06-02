#!/usr/bin/env python
# ##########################
# easy copy all necessary files of specfem3d_globe into
# target directory($runbase/specfem3d_globe).
# The second option is that you can also put all specfem stuff
# in your "$runbase/specfem3d_globe"
import os
import glob
import shutil
import yaml
from utils import copyfile


def safe_copy(fn, specfemdir, targetdir):
    origin_file = os.path.join(specfemdir, fn)
    target_file = os.path.join(targetdir, fn)

    copyfile(origin_file, target_file)


def safe_copy_model_file(specfemdir, targetdir):
    origindir = os.path.join(specfemdir, "DATABASES_MPI")
    model_files = glob.glob(os.path.join(origindir, "*"))

    if len(model_files) == 0:
        raise ValueError("No model files at dir: %s" % origindir)

    target_model_dir = os.path.join(targetdir, "DATABASES_MPI")
    if not os.path.exists(target_model_dir):
        os.makedirs(target_model_dir)

    print("-"*10 + "\nCopy model files:")
    for _file in model_files:
        print("[%s --> %s]" % (_file, target_model_dir))
        shutil.copy2(_file, target_model_dir)


def quick_check(specfemdir, filelist):
    for _file in filelist:
        path = os.path.join(specfemdir, _file)
        if not os.path.exists(path):
            raise ValueError("File not exists: %s" % (path))


def check_model_files(specfemdir):
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
    with open("config.yml") as fh:
        config = list(yaml.load_all(fh))

    targetdir = os.path.join(config[1]["runbase"], "specfem3d_globe")

    print("******************************************")
    print("Please specify the directory of specfem package.")
    print("Note that mesh files should exist before copying")
    specfemdir = raw_input("specfemdir=")
    print("target dir: %s" % targetdir)

    if not os.path.exists(specfemdir):
        raise ValueError("No specfem dir: %s" % specfemdir)

    filelist = ["bin/xspecfem3D", "OUTPUT_FILES/addressing.txt",
                "OUTPUT_FILES/values_from_mesher.h",
                "DATA/Par_file"]

    quick_check(specfemdir, filelist)
    check_model_files(specfemdir)

    print("--------------------------")
    for fn in filelist:
        safe_copy(fn, specfemdir, targetdir)

    safe_copy_model_file(specfemdir, targetdir)
