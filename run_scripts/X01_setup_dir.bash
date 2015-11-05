#!/bin/bash

# ################################################################
# Prepare files and set up directories for the source inversion
# except mesh files: for mesh file, use copy_mesh.pbs file
# System: titan.ccs.ornl.gov
# Developer: Wenjie Lei
# ################################################################

# ######################
#scratch_dir="$PROJWORK/geo018/Wenjie/SOURCE_INVERSION"
scratch_dir=".."

datacenter="$scratch_dir/DATA"

#ext=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )
ext=( "" )

#setup job dir
start_index=1
end_index=50
# #######################

date_string=`date +"%m-%d-%y_%H"`

currentdir=`pwd`

echo "current dir:" $currentdir

if [ ! -d $datacenter ];then
  echo WRONG! NO $datacenter
  exit
fi

for (( i=$start_index; i<=$end_index; i++ ))
do
  ### loop over event
  job_index_name=`printf "%03d" $i`
  echo " job_index_name: $job_index_name"
  for type in "${ext[@]}"
  do
    ### loop over type
    echo "type:$type"
    dir=$datacenter"/event_"$job_index_name"$type"
    echo $dir

    mkdir -p $dir/DATA
    mkdir -p $dir/bin
    mkdir -p $dir/OUTPUT_FILES
    mkdir -p $dir/DATABASES_MPI

    cd $currentdir
    
  done

done

echo "+++++++++++++++++++++++++++++++++++++++"
echo "+           IMPORTANT                 +"
echo "+PLEASE COPY MODEL FILES INTO RUNBASE +"
echo "+Use: qsub -q dtn copy_mesh.pbs       +"
echo "+++++++++++++++++++++++++++++++++++++++"
