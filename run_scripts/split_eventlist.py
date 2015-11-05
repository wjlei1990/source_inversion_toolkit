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

# #########################
inputfile = "XEVENTID_ALL"
njobs_bundle = 50
outputdir = "job_split_list"
output_base = "XEVENTID_"
# ########################

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
 
print "Number of events:", nevents
print "Jobs per bundle:", njobs_bundle
print "Number of jobs:", njobs

for i in range(1, njobs+1):
    print "-"*10
    print "job index:", i
    start_index = (i-1) * njobs_bundle
    end_index = min( i*njobs_bundle, nevents )
    print "event index: [%d --> %d)" % (start_index, end_index)
    outputfn = os.path.join(outputdir, "%s%d" %(output_base, i))
    print "output file:", outputfn
    with open(outputfn, 'w') as f:
        for _ind in range(start_index, end_index):
            f.write("%s\n" %eventlist[_ind])

