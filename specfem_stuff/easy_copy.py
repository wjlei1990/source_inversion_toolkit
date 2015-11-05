#!/usr/bin/env python
# ##########################
# easy copy all necessary files of specfem3d_globe into
# current directory
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
        shutil.copy2(origin_file, target_model_dir)


if __name__ == "__main__":

    specfemdir="/lustre/atlas/proj-shared/geo111/Wenjie/bm_specfem/specfem3d_globe"
    targetdir="."

    if not os.path.exists(specfemdir):
        raise ValueError("No specfem dir: %s" % specfemdir)

    filelist=["bin/xspecfem3D", "OUTPUT_FILES/addressing.txt", 
              "OUTPUT_FILES/values_from_mesher.h", "DATA/STATIONS",
              "DATA/Par_file"]

    for fn in filelist:
        safe_copy(fn, specfemdir, targetdir)

    safe_copy_model_file(specfemdir, targetdir)
