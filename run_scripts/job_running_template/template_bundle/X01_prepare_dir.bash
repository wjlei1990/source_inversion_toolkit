#!/bin/bash

#################################################################
# Prepare files and set up directories for the source inversion
# except mesh files: for mesh file, use copy_mesh.pbs file
# System: titan.ccs.ornl.gov
# Developer: Wenjie Lei
#################################################################

echo "Copy files"
./copy_files.py
ret=$?
if [ $ret -ne 0 ]; then
  echo "copy_files.py return with error"
  exit
fi

echo
echo "Generate job scripts"
./create_job_pbs.py
if [ $ret -ne 0 ]; then
  echo "create_job_pbs.py return with error"
  exit
fi

n_jobs=`ls job_solver_bundle.pbs.* | wc -l`

if [ $n_jobs -gt 0 ]; then
  echo
  echo "*******************"
  echo "Number of Jobs: $n_jobs"
  echo "*******************"
  echo
  submission_status=1
else
  echo
  echo "*******************"
  echo "No Job Scripts"
  echo "*******************"
  submission_status=0
fi

# clean up data archive dir
rm -r data/*

echo
echo "==============================="
echo "Summary"
if [ $submission_status -eq 1 ]; then
  echo "Please submit job"
else
  echo "Please check"
fi
echo "==============================="

#./submit.bash
