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

home_dir="/ccs/home/lei/SOURCE_INVERSION"

eventfile="XEVENTID"

cmtcenter="$home_dir/CMT_BIN/ALL_CMT"
specfem_dir="/lustre/atlas/proj-shared/geo111/Wenjie/bm_specfem/si_database"

datacenter="$scratch_dir/DATA"
ext=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )
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
  echo "event_ name: $line  job_index_name: $job_index_name"
  for type in "${ext[@]}"
  do
    ### loop over type
    echo "type:$type"
    cmtfile=$cmtcenter"/"$line"$type"
    dir=$datacenter"/event_"$job_index_name"$type"
    echo $cmtfile
    echo $dir
    if [ ! -f $cmtfile ]; then
      echo WRONG! no $cmtfile
    fi
    #if [ ! -d $dir ]; then
    #  echo "Dir not exists: $dir!"
    #fi
    #make simulation dir and copy files
    mkdir -p $dir/DATA
    mkdir -p $dir/bin
    mkdir -p $dir/OUTPUT_FILES
    mkdir -p $dir/DATABASES_MPI

    rm -rf $dir/OUTPUT_FILES/*
    rm -rf $dir/DATA/*

    cp $specfem_dir/DATA/Par_file $dir/DATA/
    cp $specfem_dir/OUTPUT_FILES/values_from_mesher.h $dir/OUTPUT_FILES/

    cp $specfem_dir/DATA/STATIONS $dir/DATA/
    cp $cmtfile $dir/DATA/CMTSOLUTION

    cp $specfem_dir/OUTPUT_FILES/addressing.txt $dir/OUTPUT_FILES

    cp $specfem_dir/bin/xspecfem3D $dir/bin/
    #cp $specfem_dir/bin/xmeshfem3D $dir/bin/

    ###
    ### cd to $dir and check
    ###
    cd $dir
    if [ ! -f DATA/Par_file ] ; then
      echo WRONG! No Par_file
      exit
    fi

    #if [ ! -f xparallel_forward_fullatt.sh ]; then
    #  echo WRONG! No xparallel_forward_fullatt.sh
    #  exit
    #fi
    #echo "Changing SBATCH file "
    #jobname_tag="$line""$type"
    #workdir_tag="$basedir/DATA/$jobname_tag"
    #echo "dir:$workdir_tag"
    #sed -i "s/^#SBATCH -J.*$/#SBATCH -J ${jobname_tag}/g" xparallel_forward_fullatt.sh

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
./create_job_pbs.py

n_jobs=`ls job_solver_bundle.pbs | wc -l`

if [ $n_jobs -gt 0 ]; then
  echo "*******************"
  echo "Number of Jobs: $n_jobs"
  echo "*******************"
else
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
