#!/bin/bash

#PBS -A GEO111
#PBS -N SPECFEM3D_solver
#PBS -j oe
#PBS -o job_sb.$PBS_JOBID.o
#PBS -l nodes=384
#PBS -l walltime=2:00:00

# -----------------------------------------------------
# This is a simulataneous run job submission script
# User Parameter
eventfile="XEVENTID"
runbase="/path/to/your/runbase/specfem3d_globe"
exts=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )
numproc=1
# -----------------------------------------------------

ntype=${#exts[@]}

cd $PBS_O_WORKDIR
cat $PBS_NODEFILE > compute_nodes.$PBS_JOBID
echo "$PBS_JOBID" > jobid.$PBS_JOBID

currentdir=`pwd`
echo "running simulation: `date`"
echo "Current directory: `pwd`"
echo "runbase dir: $runbase"
echo

if [ ! -d $runbase ]; then
  echo "No runbase dir found: $runbase"
  exit
fi

nevents=`cat $eventfile | wc -l`
echo "Number of events: $nevents"

ext_idx=0
eventlist=`cat $eventfile`
for ext in "${exts[@]}"
do
  echo "-------------------------------------------"
  echo "ext: $ext"

  # prepare files for each mpi run, which corresponds simultaneous run
  # of all events
  event_idx=1
  for event in ${eventlist[@]}
  do
    echo "-------"
    event_index_name=`printf "%04d" $event_idx`
    workingdir="$runbase/run_$event_index_name"
    echo "Idx $event_index_name --- event $event"
    echo "working dir $workingdir"

    ### LINK HERE
    linkbase=$currentdir"/outputbase/"$event$ext
    echo "linkbase: $linkbase"
    ln -s $linkbase"/DATA" $workingdir"/DATA"
    ln -s $linkbase"/OUTPUT_FILES" $workingdir"/OUTPUT_FILES"
    event_idx=$(( $event_idx + 1))
  done

  # job running
  echo
  echo "solver start: `date`"
  cd $runbase
  aprun -n $numproc -N1 ./bin/xspecfem3D
  cd $currentdir
  echo "solver end: `date`"

  echo "Remove symbolic links..."
  event_idx=1
  for event in ${eventlist[@]}
  do
    # UNLINK HERE
    event_index_name=`printf "%04d" $event_idx`
    workingdir="$runbase/run_$event_index_name"
    rm $workingdir"/DATA"
    rm $workingdir"/OUTPUT_FILES"

    event_idx=$(( $event_idx + 1 ))
    cd $currentdir
  done
  ext_idx=$(( $ext_idx + 1))
done

echo
echo "Check results using the script: check_job_status.pbs"
echo
echo "done: `date`"

echo -e "\n*********************************"
echo "Summary: "
echo "Total mpi runs: $ntype  finished: $ext_idx"
if [ $ntype -eq $ext_idx ]; then
  echo "Success!"
else
  echo "Fail!"
fi
echo -e "*********************************\n"
