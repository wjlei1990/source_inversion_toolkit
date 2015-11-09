#!/bin/bash

#PBS -A GEO111
#PBS -N SPECFEM3D_solver
#PBS -j oe
#PBS -o job_sb.$PBS_JOBID.o

# -----------------------------------------------------
## Job Allocation 
## titan: gpu compute nodes have 1 GPU card (K20x) and 16-core (interlagos) CPU

#PBS -l walltime=1:00:00
#PBS -l nodes=960

# -----------------------------------------------------
## User Parameter

eventfile="XEVENTID"
basedir="../.."
ext=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )

# -----------------------------------------------------

ntype=${#ext[@]}

cd $PBS_O_WORKDIR

currentdir=`pwd`

echo "running simulation: `date`"
echo "directory: `pwd`"
echo

nevents=`cat $eventfile | wc -l`
echo "Number of events: $nevents"

# obtain job information
cat $PBS_NODEFILE > compute_nodes.$PBS_JOBID
echo "$PBS_JOBID" > jobid.$PBS_JOBID

# runs simulation from 001 to nevents
echo
echo "running solver..."
echo `date`

count=0
event_index=1
for line in `cat $eventfile`
do
  event_index_name=`printf "%03d" $event_index`
  echo
  echo "-------------------------------------------"
  echo "event:$line  event_index: $event_index_name"
  for type in "${ext[@]}"
  do
    workingdir="$basedir/DATA/event_$event_index_name$type"
    echo "working dir: $workingdir"
    cd $workingdir
    echo "Actual working dir: `pwd`"
    echo "Executable: `ls ./bin/xspecfem3D`"

    # number of proc
    NPROC_XI=`grep NPROC_XI DATA/Par_file | cut -d = -f 2 `
    NPROC_ETA=`grep NPROC_ETA DATA/Par_file | cut -d = -f 2`
    NCHUNKS=`grep NCHUNKS DATA/Par_file | cut -d = -f 2 `
    numproc=$(( $NCHUNKS * $NPROC_XI * $NPROC_ETA ))

    # stores setup
    cp DATA/Par_file OUTPUT_FILES/
    cp DATA/CMTSOLUTION OUTPUT_FILES/
    cp DATA/STATIONS OUTPUT_FILES/

    # job running
    aprun -n $numproc -N1 ./bin/xspecfem3D &

    count=$(( $count + 1 ))
    cd $currentdir
    echo "job done at: `date`"
  done
  event_index=$(( $event_index + 1 ))
done

wait

total_jobs=$(( $nevents*$ntype ))

echo
echo "Check results using the script: check_job_status.pbs"
echo
echo "done: `date`"

echo -e "\n*********************************"
echo "Summary: "
echo "Total job: $total_jobs  finished: $count"
if [ $total_jobs -eq $count ]; then
  echo "Success!"
else
  echo "Fail!"
fi
echo -e "*********************************\n"
