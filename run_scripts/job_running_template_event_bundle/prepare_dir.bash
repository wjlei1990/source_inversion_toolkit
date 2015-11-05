#!/bin/bash

#################################################################
# Prepare files and set up directories for the source inversion
# except mesh files: for mesh file, use copy_mesh.pbs file
# System: titan.ccs.ornl.gov
# Developer: Wenjie Lei
#################################################################

#######################
#scratch_dir="$PROJWORK/geo018/Wenjie/SOURCE_INVERSION"
scratch_dir="../.."

eventfile="XEVENTID"

cmtcenter="/ccs/home/lei/SOURCE_INVERSION/CMT_BIN/ALL_CMT"

specfem_dir="$scratch_dir/specfem_stuff"
datacenter="$scratch_dir/DATA"

#ext=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )
ext=( "" )
########################

date_string=`date +"%m-%d-%y_%H"`

currentdir=`pwd`
echo "current dir:" $currentdir

if [ ! -f $eventfile ]; then
  echo WRONG! NO $eventfile
  exit
fi

if [ ! -d $cmtcenter ]; then
  echo WRONG! NO $cmtcenter
  exit
fi

if [ ! -d $datacenter ];then
  echo WRONG! NO $datacenter
  exit
fi

#setup job dir
job_index=0
while read line
do
  ### loop over event
  job_index=$(( $job_index+1 ))
  job_index_name=`printf "%03d" $job_index`
  echo "----------------------"
  echo "event_name: $line  job_index_name: $job_index_name"
  for type in "${ext[@]}"
  do
    ### loop over type
    echo "type:$type"
    cmtfile=$cmtcenter"/"$line"$type"
    dir=$datacenter"/event_"$job_index_name"$type"
    echo "cmtfile:" $cmtfile
    echo "target dir:" $dir
    if [ ! -f $cmtfile ]; then
      echo WRONG! no $cmtfile
    fi
    #if [ ! -d $dir ]; then
    #  echo "Dir not exists: $dir!"
    #fi
    #make simulation dir and copy files
    rm -r $dir/DATA
    rm -r $dir/bin
    rm -r $dir/OUTPUT_FILES

    cp -r $specfem_dir/DATA $dir
    cp -r $specfem_dir/bin $dir
    cp -r $specfem_dir/OUTPUT_FILES $dir

    cp $cmtfile $dir/DATA/CMTSOLUTION

    # cd to $dir and check
    cd $dir
    if [ ! -f DATA/Par_file ] ; then
      echo WRONG! No Par_file
      exit
    fi

    if [ ! -f ./bin/xspecfem3D ] ; then
      echo WRONG! No xspecfem3D
      exit
    fi

    cd $currentdir
    
  done

done < $eventfile

submission_status=1
#########
# generate the job submission script
echo
./create_job_pbs.py

n_jobs=`ls job_solver_bundle.pbs.* | wc -l`

if [ $n_jobs -gt 0 ]; then
  echo
  echo "*******************"
  echo "Number of Jobs: $n_jobs"
  echo "*******************"
  echo
else
  echo
  echo "*******************"
  echo "No Job Scripts"
  echo "*******************"
  submission_status=0
fi

########
# check the mesh file and submit the job
echo 
echo "Check mesh file...Using check_mesh_status.bash"
echo

./check_mesh_status.bash > mesh.log

status_string=`grep "Final Status" mesh.log`

if [[ $status_string == *Success* ]]; then
  echo "Bingo! Mesh file Ready!"
else
  echo "Alert: Mesh not ready!"
  submission_status=0
fi

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
