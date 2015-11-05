#!/bin/bash
# #########################################################
# Copy all necessary job submission files into a directory
# so you make use of it directly.
# #########################################################

echo "======================================"
echo "Split large eventlist into small(workable) ones"
./split_eventlist.py

echo "======================================"
echo "Create job submission sub folder"
# User parameter
tag="test_benchmark"
job_template_dir="job_running_template_event_bundle"

njobs=`ls job_split_list/* | wc -l`

echo "Number of jobs: $njobs"

for(( i=1; i<=$njobs; i++ ))
do
  target_dir="job_"$tag"_$i"
  echo "Sub job dir: $target_dir" 
  mkdir -p $target_dir
  cp $job_template_dir/* $target_dir
  cp job_split_list/XEVENTID_$i $target_dir/XEVENTID
done
