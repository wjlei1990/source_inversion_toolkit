#!/usr/bin/env python
# #######################################################
# Script that generate the job submission scripts on titan
# using the original job_template. For example, you have 50
# events in the XEVENTID file. But you may not want to submie
# such a big job at one time. So you want to run maybe 3
# events one time. This scripts help you to split you big
# job into smaller ones.
# #######################################################

import os
import glob
import math
import re
from utils import read_txt_into_list
import yaml


def write_list_to_txt(vlist, filename):
    with open(filename, 'w') as f:
        for value in vlist:
            f.write("%s\n" % value)


def modify_job_sbatch_file(inputfile, outputfile, eventfile, start_idx,
                           nnodes, walltime, deriv_cmt_list):
    fi = open(inputfile, "r")
    fo = open(outputfile, "w")

    content = fi.readlines()

    full_ext_list = ["Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp",
                     "dep", "lon", "lat"]

    ext_list = "ext=( \"\" "
    for _ext in deriv_cmt_list:
        if _ext not in full_ext_list:
            raise ValueError("ext incorrect: %s" % _ext)
        ext_list += "\"_%s\" " % _ext
    ext_list += ")"
    print "ext_list:", ext_list

    for line in content:
        line = re.sub(r"^#PBS -l nodes=.*", "#PBS -l nodes=%d" %
                      nnodes, line)
        line = re.sub(r"^#PBS -l walltime=.*", "#PBS -l walltime=%s" %
                      walltime, line)
        line = re.sub(r"^eventfile=.*", "eventfile=\"%s\"" %
                      eventfile, line)
        line = re.sub(r"^event_index=.*", "event_index=%d" %
                      (start_idx+1), line)
        line = re.sub(r"^ext=.*", ext_list, line)

        # turn of waiting mode
        line = re.sub(r"./bin/xspecfem3D &", "./bin/xspecfem3D", line)
        line = re.sub(r"^wait", "#wait", line)

        fo.write(line)


def create_job_pbs(nevents_per_job, walltime_per_simulation, deriv_cmt_list):

    nnodes_per_simulation = extract_number_of_nodes()
    # User parameter
    walltime = "%d:00:00" % int(walltime_per_simulation*nevents_per_job)

    eventlist_file = "./XEVENTID"
    job_template = "job_solver_bundle.init.bash"

    sub_eventfile_prefix = "XEVENTID_"
    sub_sbatch_prefix = "job_solver_bundle.pbs."

    # remove old files
    filelist = glob.glob(sub_eventfile_prefix+"*")
    for fn in filelist:
        os.remove(fn)
    filelist = glob.glob(sub_sbatch_prefix+"*")
    for fn in filelist:
        os.remove(fn)

    eventlist = read_txt_into_list(eventlist_file)
    nevents = len(eventlist)
    njobs = int(math.ceil(float(nevents) / nevents_per_job))

    print "====== Create job scripts ======="
    print "Number of events:", nevents
    print "Number of jobs:", njobs

    for ijob in range(njobs):
        # determine index
        print "-----------"
        print "Jobid: %d" % (ijob + 1)
        start_idx = ijob * nevents_per_job
        end_idx = (ijob + 1) * nevents_per_job
        if ijob == njobs-1:
            end_idx = nevents
        print "start and end idx: [%d, %d)" % (start_idx, end_idx)

        # create sub-eventlist file
        eventfile = "%s%d" % (sub_eventfile_prefix, ijob+1)
        print "eventlist file: %s" % eventfile
        write_list_to_txt(eventlist[start_idx:end_idx], eventfile)

        # create job pbs script
        outputfn = "%s%d" % (sub_sbatch_prefix, ijob+1)
        print "jobs batch file: %s" % outputfn
        modify_job_sbatch_file(job_template, outputfn, eventfile, start_idx,
                               nnodes_per_simulation, walltime, deriv_cmt_list)


def extract_number_of_nodes():
    specfem_parfile = "../../specfem_stuff/DATA/Par_file"
    with open(specfem_parfile) as fh:
        content = fh.readlines()
    for line in content:
        if re.search(r'^NPROC_XI', line):
            nproc_xi = int(line.split()[-1])
        if re.search(r'^NPROC_ETA', line):
            nproc_eta = int(line.split()[-1])
        if re.search(r'^NCHUNKS', line):
            nchunks = int(line.split()[-1])
    nproc = nproc_xi * nproc_eta * nchunks
    return nproc

if __name__ == "__main__":
    with open("./config.yaml") as fh:
        config = yaml.load(fh)
    nevents_per_job = config["nevents_per_job"]
    walltime_per_simulation = config["walltime_per_simulation"]
    create_job_pbs(nevents_per_job, walltime_per_simulation)
