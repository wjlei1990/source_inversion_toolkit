#!/bin/bash

fn_base="job_solver_bundle.pbs"

n_jobs=`ls job_solver_bundle.pbs.* | wc -l`

echo "Number of jobs: $n_jobs"

for(( i=1; i<=$n_jobs; i++ ))
do
  echo $i
  file=$fn_base".$i"
  echo "$file"
  qsub $file
done
