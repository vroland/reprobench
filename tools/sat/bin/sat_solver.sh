#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0
thp=0
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

if [ ! -f $filename ] ; then
  echo "Filename does not exist. Exiting..."
  exit 1
fi

if [ $thp == 1 ] ; then
  env="GLIBC_THP_ALWAYS=1"
fi

echo $env

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

if [ "$solver" == "plingeling" ] ; then
  solver_cmd="./"$solver"_glibc -t 1 -g 8 $@"
#elif [ "$solver" == "mergesat" ] ; then
else
  solver_cmd="./$solver"_glibc $@
fi

cd "$(dirname "$0")"
echo "$cmd | env $env $solver_cmd"
$cmd | $solver_cmd &
PID=$!
wait $PID
exit $?

