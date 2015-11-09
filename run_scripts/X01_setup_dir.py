#!/usr/bin/env python
# ################################################################
# Prepare files and set up directories for the source inversion
# except mesh files: for mesh file, use copy_mesh.pbs file
# System: titan.ccs.ornl.gov
# Developer: Wenjie Lei
# ################################################################

import yaml
import os

def safe_makedir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

if __name__ == "__main__":

    with open("config.yaml") as fh:
        config = yaml.load(fh)

    runbase_size = config["runbase_size"]
    scratch_dir=".."
    runbase=os.path.join(scratch_dir, "RUN_BASE")

    for _idx in range(runbase_size):
        idx = _idx + 1 
        print("Seting up index: %d" % idx)
        dirname = os.path.join(runbase, "event_%03d" % idx)
        print("Dir path: %s" % dirname)
        safe_makedir(os.path.join(dirname, "DATA"))
        safe_makedir(os.path.join(dirname, "bin"))
        safe_makedir(os.path.join(dirname, "OUTPUT_FILES"))
        safe_makedir(os.path.join(dirname, "DATABASES_MPI"))

