#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0

while getopts "h?vtf:l:" opt; do
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
    l)  lp=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

trap 'kill -TERM $PID' TERM

cat /etc/hostname

echo /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/enabled

if [ ! -z $thp ] ; then
  export GLIBC_THP_ALWAYS=1
  echo "Using THP option in libc"
fi


if [ -z $filename ] ; then
  echo "No filename given. Exiting..."
  exit 1
fi

if [ ! -f $filename ] ; then
  echo "Filename does not exist. Exiting..."
  exit 1
fi

if [ -z $lp ] ; then
  echo "No logic program (-l) given. Exiting..."
  exit 1
fi

if [ ! -f $lp ] ; then
  echo "Logic program does not exist. Exiting..."
  exit 1
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

solver_cmd="./clasp_glibc" $@

cd "$(dirname "$0")"
echo "$cmd | env $env $solver_cmd"
$cmd | ./gringo - $lp | $solver_cmd &

PID=$!
wait $PID
exit $?
