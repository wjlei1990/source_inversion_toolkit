#!/bin/bash

#PBS -A GEO111
#PBS -N SPECFEM3D_solver
#PBS -j oe
#PBS -o job_sb.$PBS_JOBID.o

# -----------------------------------------------------
## Job Allocation 
## titan: gpu compute nodes have 1 GPU card (K20x) and 16-core (interlagos) CPU

#PBS -l walltime=2:00:00
#PBS -l nodes=384

# -----------------------------------------------------
## User Parameter

eventfile="XEVENTID"
runbase="../../RUN_BASE"
ext=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )

event_index=1
# -----------------------------------------------------

ntype=${#ext[@]}

cd $PBS_O_WORKDIR
# obtain job information
cat $PBS_NODEFILE > compute_nodes.$PBS_JOBID
echo "$PBS_JOBID" > jobid.$PBS_JOBID

currentdir=`pwd`

echo "running simulation: `date`"
echo "Current directory: `pwd`"
echo

nevents=`cat $eventfile | wc -l`
echo "Number of events: $nevents"

count=0
eventlist=`cat $eventfile`
for event in ${eventlist[@]}
do
  event_index_name=`printf "%03d" $event_index`
  echo
  echo "-------------------------------------------"
  echo "event:$event  event_index: $event_index_name"
  for type in "${ext[@]}"
  do
    workingdir="$runbase/event_$event_index_name"
    echo "============"
    echo "type: $type"
    echo "working dir: $workingdir"

    # copy cmtfile
    cmtfile="cmtfile/$event$type"
    cp $cmtfile $workingdir/DATA/CMTSOLUTION

    # copy station file
    stafile="station/"$event".STATIONS"
    cp $stafile $workingdir/DATA/STATIONS

    cd $workingdir
    echo "Actual working dir: `pwd`"
    echo "Executable: `ls ./bin/xspecfem3D`"

    # number of proc
    NPROC_XI=`grep NPROC_XI DATA/Par_file | cut -d = -f 2 `
    NPROC_ETA=`grep NPROC_ETA DATA/Par_file | cut -d = -f 2`
    NCHUNKS=`grep NCHUNKS DATA/Par_file | cut -d = -f 2 `
    numproc=$(( $NCHUNKS * $NPROC_XI * $NPROC_ETA ))

    # job running
    echo "solver start: `date`"
    aprun -n $numproc -N1 ./bin/xspecfem3D &
    echo "solver end: `date`"

    # mv OUTPUT_FILES out
    archivedir=$currentdir"/data/$event$type"
    echo "data stored at: $archivedir"
    mkdir -p $archivedir
    rm $archivedir/*

    # stores setup
    mv DATA/CMTSOLUTION OUTPUT_FILES/
    cp DATA/Par_file OUTPUT_FILES/
    cp DATA/STATIONS OUTPUT_FILES/

    mv OUTPUT_FILES/*.sac $archivedir
    mv OUTPUT_FILES/*.h5 $archivedir
    cp OUTPUT_FILES/* $archivedir
  
    count=$(( $count + 1 ))
    echo "job done at: `date`"

    cd $currentdir
  done
  event_index=$(( $event_index + 1 ))
done

#wait

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
