#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0

while getopts "h?vt:s:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=1
        ;;
    t)  thp=1
        ;;
    esac
done

shift $((OPTIND-1))

trap 'kill -TERM $PID' TERM

echo /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/enabled

if [ ! -z $thp ] ; then
  export GLIBC_THP_ALWAYS=1
  echo "Using THP option in libc"
fi
cmd="./clasp_glibc $@"
echo $cmd

cd "$(dirname "$0")"
bash -c "$cmd" &
PID=$!
wait $PID
exit $?

