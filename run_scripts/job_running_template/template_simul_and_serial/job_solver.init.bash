#!/bin/bash

#PBS -A GEO111
#PBS -N SPECFEM3D_solver
#PBS -j oe
#PBS -m a
#PBS -m b
#PBS -m e
#PBS -M lei@princeton.edu
#PBS -o job_sb.$PBS_JOBID.o
#PBS -l nodes=384
#PBS -l walltime=2:00:00

# -----------------------------------------------------
# This is a simulataneous and serial job script
# for example, you have 250 events and 50 simultaneous run
# So it needs to loop 5 times in serial, inside which 50
# simultaneous runs
# User Parameter
total_serial_runs=5
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

for (( serial_id=1; serial_id<=$total_serial_runs; serial_id++ ))
do
  echo "***********************************************************"
  echo "Serial run id: $serial_id"
  # begein serial
  eventfile="XEVENTID.$serial_id"
  eventlist=`cat $eventfile`
  nevents=`cat $eventfile | wc -l`
  echo "Eventfile: $eventfile"
  echo "Number of events: $nevents"
  for ext in "${exts[@]}"
  do
    echo "===================================="
    echo "EXT: $ext"
    # ############################################
    # prepare files for each mpi run, which corresponds simultaneous run
    # of all events
    event_idx=1
    for event in ${eventlist[@]}
    do
      echo "-------"
      event_index_name=`printf "%04d" $event_idx`
      workingdir="$runbase/run$event_index_name"
      echo "Idx: $event_index_name --- event $event"
      echo "working dir: $workingdir"

      ### LINK HERE
      linkbase=$currentdir"/outputbase/"$event$ext
      echo "linkbase: $linkbase"
      ln -s $linkbase"/DATA" $workingdir"/DATA"
      ln -s $linkbase"/OUTPUT_FILES" $workingdir"/OUTPUT_FILES"
      event_idx=$(( $event_idx + 1))
    done

    # ############################################
    # job running
    cd $runbase
    echo
    echo "pwd: `pwd`"
    #ls -alh
    echo "solver start: `date`"
    aprun -n $numproc -N1 ./bin/xspecfem3D
    echo "solver end: `date`"
    cd $currentdir

    # ############################################
    # Unlink
    echo "Remove symbolic links..."
    event_idx=1
    for event in ${eventlist[@]}
    do
      # UNLINK HERE
      event_index_name=`printf "%04d" $event_idx`
      workingdir="$runbase/run$event_index_name"
      rm $workingdir"/DATA"
      rm $workingdir"/OUTPUT_FILES"

      event_idx=$(( $event_idx + 1 ))
      cd $currentdir
    done
    # end of one eventlist file
  done
  # end of extension
done
# end of all eventlist files

echo
echo "Check results using the script: check_job_status.pbs"
echo
echo "done: `date`"

echo -e "\n*********************************"
echo "Summary: "
echo "Success!"
echo -e "*********************************\n"
