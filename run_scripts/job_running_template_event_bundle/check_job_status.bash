#!/bin/bash
############################################################################
# Batch script to check the output(job status) for events in current XEVENTID file
############################################################################

######################
#workdir=$MEMBERWORK/geo018/SOURCE_INVERSION/DATA
workdir="../../DATA"

eventfile="XEVENTID"

ext=( "" )
######################

### check the number of events
nevents=`cat $eventfile | wc -l`
echo "number of events: $nevents"
if [ $nevents -eq 0 ]; then
  echo "0 event. Check XEVENTID file!"
  exit
else 
  echo "Nevents: $nevents"
fi

ntype=${#ext[@]}

if [ ! -f $eventfile ]; then
  echo WRONG! NO $eventfile
  exit
fi

echo 
echo "Check Job Status..."
echo

event_index=0
event_unfinished=0
while read line
do
  event_index=$(( $event_index + 1 ))
  event_index_name=`printf "%03d" $event_index`
  ### loop over event
  echo "event: $line  event_index: $event_index_name"
  echo "mesh center: $meshcenter"
  job_unfinished=0
  for type in "${ext[@]}"
  do
    ### loop over type
    #echo "type:$type"
    targetdir=$workdir"/event_"$event_index_name$type"/OUTPUT_FILES"
    #echo "targetdir: $targetdir"

    #check
    if [ ! -d $targetdir ]; then
      echo "Dir not exist: $targetdir"
      exit
    fi
    if [ ! -f $targetdir/AAK.*Z.sem.sac ]; then
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

done < $eventfile

echo -e "\n*********************************"
echo "Summary: "
echo "Total event: $nevents  Unfished: $event_unfinished"
echo -e "*********************************\n"

