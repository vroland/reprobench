#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0

while getopts "h?vt:s:f:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=1
        ;;
    t)  thp=1
        ;;
    f)  filename=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

function interrupted(){
  kill -TERM $PID
  echo "Received signal..."
}
trap interrupted TERM
trap interrupted INT

if [ ! -z $thp ] ; then
  export GLIBC_THP_ALWAYS=1
  echo "Using THP option in libc"
fi

cd "$(dirname "$0")"
#get basic info
source ../../../bash_shared/sysinfo.sh
#get file transparently from compressed file and temporarily store in shm
source ../../../bash_shared/tcat.sh


solver_cmd="./clasp_glibc" $@
echo "cat $decomp_filename | env $env $solver_cmd"
#run call in background and wait for finishing
cat $decomp_filename | $solver_cmd &
PID=$!
wait $PID
exit $?
