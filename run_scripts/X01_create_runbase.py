#!/usr/bin/env python
# ################################################################
# Set up directories for the source inversion
# except specfem related files: for those files, use copy_mesh.pbs file
# Developer: Wenjie Lei
# -------------------
# Directory structure:
#   runbase/
#     archive/           # archive directory to store output data
#     jobs/              # directory of job scripts
#     specfem3d_globe/   # specfem directory
#       DATA/
#       bin/
#       OUTPUT_FILES/
#       DATABASES_MPI/
# ################################################################
from __future__ import print_function, division
import yaml
import os
from utils import safe_makedir


def check_config(config):
    running_mode = config[1]["running_mode"]
    if running_mode != "simul":
        raise ValueError("Only running_mode 'simul' is allowed")

    nevents_per_mpirun = config[1]["nevents_per_mpirun"]
    if nevents_per_mpirun <= 1:
        raise ValueError("nevents_per_mpirun should be larger than 1")


def create_runbase(runbase):
    print("Create runbase at dir: %s" % runbase)
    if not os.path.exists(runbase):
        os.makedirs(runbase)

    # make archive dir
    safe_makedir(os.path.join(runbase, "archive"))

    # make job scripts dir
    safe_makedir(os.path.join(runbase, "jobs"))

    # make specfem base dir
    specfemdir = os.path.join(runbase, "specfem3d_globe")
    safe_makedir(specfemdir)
    safe_makedir(os.path.join(specfemdir, "DATA"))
    safe_makedir(os.path.join(specfemdir, "bin"))
    safe_makedir(os.path.join(specfemdir, "OUTPUT_FILES"))
    safe_makedir(os.path.join(specfemdir, "DATABASES_MPI"))

if __name__ == "__main__":

    with open("config.yml") as fh:
        config = list(yaml.load_all(fh))

    check_config(config)

    runbase = config[1]["runbase"]
    create_runbase(runbase)
