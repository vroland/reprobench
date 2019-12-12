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

if [ -z $solver ] ; then
  echo "No Solver given. Exiting..."
  exit 1
fi
solver_cmd="./$solver"_glibc $@

if [ ! -z $thp ] ; then
  echo "No filename given. Exiting..."
  exit 1
fi

if [ -n $thp ] ; then
  export GLIBC_THP_ALWAYS=1
  echo "Using THP option in libc"
fi

type=$(file -b --mime-type $filename)
echo $type

if [ $type == "application/x-lzma" ] ; then
  cmd="lzcat $filename"
elif [ $type == "application/x-bzip2" ] ; then
  cmd="bzcat $filename"
elif [ $type == "application/x-xz" ] ; then
  cmd="xzcat $filename"
else
  cmd="zcat -f $filename"
fi


cd "$(dirname "$0")"
echo "$cmd | $solver_cmd"
echo GLIBC_THP_ALWAYS=$GLIBC_THP_ALWAYS
$cmd | $solver_cmd &
PID=$!
wait $PID
exit $?

