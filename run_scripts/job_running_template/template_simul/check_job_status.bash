#!/bin/bash
############################################################################
# Batch script to check the output(job status) for events in current XEVENTID file
############################################################################

######################
workdir="./data"

eventfile="XEVENTID"

ext=( "" "_Mrr" "_Mtt" "_Mpp" "_Mrt" "_Mrp" "_Mtp" "_dep" "_lat" "_lon" )
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
while read event
do
  ### loop over event
  echo "event: $event"
  job_unfinished=0
  for type in "${ext[@]}"
  do
    ### loop over type
    targetdir=$workdir"/"$event$type
    echo $targetdir

    #check
    if [ ! -d $targetdir ]; then
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

if [ $event_unfinished -eq 0 ]; then
  echo "Success" > job.log
else
  echo "Fail" > job.log
fi

