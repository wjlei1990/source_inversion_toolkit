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

# User parameter
nevents_per_job = 1
nnodes_per_job = 384
walltime = "%d:00:00" % int(2*nevents_per_job)
eventlist_file = "./XEVENTID"
job_template = "job_solver_bundle.init.bash"


def read_txt_to_list(filename):
    with open(filename, 'r') as f:
        content = f.readlines()
        return [ line.rstrip('\n') for line in content ] 


def write_list_to_txt(vlist, filename):
    with open(filename, 'w') as f:
        for value in vlist:
            f.write("%s\n" % value)


def modify_job_sbatch_file(inputfile, outputfile, eventfile, start_idx):
    fi = open(inputfile, "r")
    fo = open(outputfile, "w")

    content = fi.readlines()

    for line in content:
        line = re.sub(r"^#PBS -l nodes=.*", "#PBS -l nodes=%d" % 
                      nnodes_per_job, line)
        line = re.sub(r"^#PBS -l walltime=.*", "#PBS -l walltime=%s" % 
                      walltime, line)
        line = re.sub(r"^eventfile=.*", "eventfile=\"%s\"" % 
                      eventfile, line)
        line = re.sub(r"^event_index=.*", "event_index=%d" % 
                      (start_idx+1), line)

        # turn of waiting mode
        line = re.sub(r"./bin/xspecfem3D &", "./bin/xspecfem3D", line)
        line = re.sub(r"^wait", "#wait", line)

        fo.write(line) 


def create_job_pbs():
    sub_eventfile_prefix = "XEVENTID_"
    sub_sbatch_prefix = "job_solver_bundle.pbs."

    # remove old files 
    filelist = glob.glob(sub_eventfile_prefix+"*")
    for fn in filelist:
        os.remove(fn)
    filelist = glob.glob(sub_sbatch_prefix+"*")
    for fn in filelist:
        os.remove(fn)

    eventlist = read_txt_to_list(eventlist_file)
    nevents = len(eventlist)
    njobs = int(math.ceil( float(nevents) / nevents_per_job))

    print "====== Create job scripts ======="
    print "Number of events:", nevents 
    print "Number of jobs:", njobs

    for ijob in range(njobs):
        # determine index
        print "-----------"
        print "Jobid: %d" % ijob
        start_idx = ijob * nevents_per_job 
        end_idx = (ijob + 1) * nevents_per_job
        if ijob == njobs-1:
            end_idx = nevents
        print "start and end idx: [%d, %d]" % (start_idx, end_idx)

        # create sub-eventlist file
        eventfile = "%s%d" %(sub_eventfile_prefix, ijob+1)
        print "eventlist file: %s" % eventfile
        write_list_to_txt(eventlist[start_idx:end_idx], eventfile)

        # create job pbs script
        outputfn = "%s%d" %(sub_sbatch_prefix, ijob+1)
        print "jobs batch file: %s" % outputfn
        modify_job_sbatch_file(job_template, outputfn, eventfile, start_idx)


if __name__ == "__main__":
    create_job_pbs()
