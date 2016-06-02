#!/bin/bash

job_script="job_solver.bash"
if [ ! -f $job_script ]; then
  echo "No $job_script found"
  exit
fi

echo "job submitted!"
qsub -q titan job_solver.bash
