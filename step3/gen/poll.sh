#!/bin/bash
# usage: poll.sh SINCE_ISO "q001 q002 ..." MIN_WAIT_MIN MAX_WAIT_MIN
cd ~/didigou/autofinbench/repo
SINCE="$1"; QS="$2"; MINW=$(( $3*60 )); MAXW=$(( $4*60 )); T0=$(date +%s); N=$(echo $QS | wc -w)
while true; do
  sleep 300
  git fetch -q origin 2>/dev/null
  UPD=$(git log origin/main --since="$SINCE" --name-only --format= -- step3/answers | grep -o 'q[0-9]*' | sort -u)
  GOT=0; for q in $QS; do echo "$UPD" | grep -qx "$q" && GOT=$((GOT+1)); done
  EL=$(( $(date +%s)-T0 ))
  echo "$(date +%H:%M) answered $GOT/$N"
  if [ $GOT -ge $N ] || { [ $EL -ge $MINW ] && [ $GOT -ge 1 ]; } || [ $EL -ge $MAXW ]; then
    echo "DONE answered=$GOT/$N: $(echo $UPD | tr '\n' ' ')"; exit 0; fi
done
