#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0

while getopts "h?vtf:e:" opt; do
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
    l)  encoding=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

trap 'kill -TERM $PID' TERM

if [ ! -z $thp ] ; then
  echo "Using THP option in libc"
  env=GLIBC_THP_ALWAYS=1
fi

if [ -z $filename ] ; then
  echo "No filename given. Exiting..."
  exit 1
fi

if [ ! -f $filename ] ; then
  echo "Filename does not exist. Exiting..."
  exit 1
fi

if [ -z $encoding ] ; then
  echo "No encoding (-e) given. Exiting..."
  exit 1
fi

if [ ! -f $encoding ] ; then
  echo "Encoding does not exist. Exiting..."
  exit 1
fi


cd "$(dirname "$0")"
#get basic info
source ../../../bash_shared/sysinfo.sh

solver_cmd="./clasp_glibc" $@

cd "$(dirname "$0")"
echo "./gringo $filename $encoding | $solver_cmd"
#run call in background and wait for finishing
env $env ./gringo $filename $encoding | $solver_cmd &

PID=$!
wait $PID
exit $?
