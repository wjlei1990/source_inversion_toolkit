#!/bin/bash
############################################################################
# Batch script to check the output(job status) for events in current XEVENTID file
############################################################################

#################################
#workdir=$PROJWORK/geo018/Wenjie/SOURCE_INVERSION/DATA
workdir="../../DATA"

ext=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )
#################################

### check the number of events
nevents=`cat XEVENTID | wc -l`
echo "nevents: $nevents"

ntype=${#ext[@]}

echo 
echo "Check Mesh Status..."
echo

event_unfinished=0
for (( event_index=1; event_index<=$nevents; event_index++ ))
do
  event_index_name=`printf "%03d" $event_index`
  ### loop over event
  echo "event: $line  event_index: $event_index_name"
  echo "mesh center: $meshcenter"
  job_unfinished=0
  for type in "${ext[@]}"
  do
    ### loop over type
    #echo "type:$type"
    targetdir=$workdir"/event_"$event_index_name$type"/DATABASES_MPI"
    #echo "targetdir: $targetdir"

    #check
    if [ ! -d $targetdir ]; then
      echo "Dir not exist: $targetdir"
      exit
    fi
    nmesh_file=`ls $targetdir | wc -l`
    #echo "nmesh_file: $nmesh_file"
    if [ $nmesh_file -lt 5 ]; then
      job_unfinished=$(( $job_unfinished+1 ))
    fi
  done

  echo "Unfinished: $job_unfinished  Total: $ntype "
  
  if [ $job_unfinished -eq 0 ]; then
    echo "Done!"
  else
    echo "Not yet Done: $job_unfinished"
    event_unfinished=$(( $event_unfinished + 1 ))
  fi

done

echo -e "\n*********************************"
echo "Summary: "
echo "Total event: $nevents  No mesh file: $event_unfinished"
if [ $event_unfinished -eq 0 ]; then
  echo "Final Status: Success"
else
  echo "Final Status: Fail"
fi

echo -e "*********************************\n"

