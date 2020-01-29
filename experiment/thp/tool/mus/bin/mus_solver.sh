#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0
while getopts "h?vts:f:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=1
        ;;
    t)  thp=1
        ;;
    s)  solver=$OPTARG
        ;;
    f)  filename=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

trap 'kill -TERM $PID' TERM

cat /etc/hostname

echo /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/enabled

if [ -z $solver ] ; then
  echo "No Solver given. Exiting..."
  exit 1
fi

if [ -z $filename ] ; then
  echo "No filename given. Exiting..."
  exit 1
fi

if [ ! -z $thp ] ; then
  export GLIBC_THP_ALWAYS=1
  echo "Using THP option in libc"
fi
cmd="./"$solver"_glibc $@ $filename"
echo $cmd

cd "$(dirname "$0")"
bash -c 'echo GLIBC_THP_ALWAYS=$GLIBC_THP_ALWAYS'
bash -c "$cmd" &
PID=$!
wait $PID
exit $?

