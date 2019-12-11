#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0

while getopts "h?vg:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=1
        ;;
    g)  glibc=1
        ;;
    esac
done

shift $((OPTIND-1))

trap 'kill -TERM $PID' TERM

if [ -n $verbose ] ; then
  cmd="./clasp_glibc $@"
else
  cmd="./clasp $@"
fi
echo $cmd

cd "$(dirname "$0")"
bash -c "$cmd" &
PID=$!
wait $PID
exit $?

