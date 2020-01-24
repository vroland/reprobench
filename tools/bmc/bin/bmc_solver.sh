#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0
thp=0
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

function interrupted(){
  kill -TERM $PID
}
trap interrupted TERM
trap interrupted INT

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
  env=GLIBC_THP_ALWAYS=1
fi

cd "$(dirname "$0")"

#get basic info
source ../../bash_shared/sysinfo.sh

cwd=$(pwd)
# so far no compression here
if [ "$solver" == "aigbmc" ] ; then
  solver_cmd="./"$solver"_glibc $@ -m -n 100 $filename"
elif [ "$solver" == "cbmc" ] ; then
  #crappy path fix for the tool calls
  #TODO: needs to be fixed somehow
  #TODO: think of a better way to handle those cases with the benchmark tool
  fdir=$(dirname $filename)
  params=$(cat $filename | sed "s|\$BENCHDIR/|"$fdir"/|g")
  solver_cmd=$cwd"/"$solver"_glibc $@ $params"
else
  echo 'Default parameters for solver undefined'
  exit 1
fi

#TODO: fixme
cd /scratch/p_gpusat/automated-reasoner-builds/benchmarks/SWMC_llbmc_1.1/
echo "env $env $solver_cmd $filename"
echo
echo
env $env $solver_cmd &

PID=$!
wait $PID
exit $?
