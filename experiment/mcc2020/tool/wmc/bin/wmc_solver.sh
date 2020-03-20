#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
#verbose=0
thp=0
preprocessor="none"
while getopts "h?vt:s:f:i:p:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  echo "Currently unsupported."
        #verbose=1
        ;;
    t)  thp=$OPTARG
        ;;
    s)  solver=$OPTARG
        ;;
    f)  filename=$OPTARG
        ;;
    i)  original_input=$OPTARG
        ;;
    p)  preprocessor=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

function interrupted(){
  kill -TERM $PID
}
trap interrupted TERM
trap interrupted INT


if [ -z "$solver" ] ; then
  echo "No Solver given. Exiting..."
  exit 1
fi

if [ -z "$filename" ] ; then
  echo "No filename given. Exiting..."
  exit 1
fi

if [ ! -f "$filename" ] ; then
  echo "Filename does not exist. Exiting..."
  exit 1
fi

if [ "$thp" == 1 ] ; then
  env=GLIBC_THP_ALWAYS=1
else
  env=VOID=1
fi

cd "$(dirname "$0")" || (echo "Could not change directory to $0. Exiting..."; exit 1)


if [ "$solver" == "approxmc" ] ; then
  solver_cmd="./approxmc_glibc $*"
elif [ "$solver" == "c2d" ] ; then
  solver_cmd="./c2d $* -count -in_memory -smooth_all -in "
elif [ "$solver" == "cachet" ] ; then
  solver_cmd="./cachet_glibc $*"
elif [ "$solver" == "d4" ] ; then
  solver_cmd="./d4 $*"
elif [ "$solver" == "ganak" ] ; then
  solver_cmd="./ganak_glibc -p $*"
elif [ "$solver" == "minic2d" ] ; then
  solver_cmd="./minic2d_glibc -C $* -c"
elif [ "$solver" == "sharpsat" ] ; then
  solver_cmd="./sharpsat_glibc $*"
else
  solver_cmd="./"$solver"_glibc $*"
fi


echo "Original input instance was $original_input"
echo "env $env $solver_cmd $filename"
echo
echo


#NOTE: if you need to redirect the solver output in the future, we suggest to use stdlog.txt
#
# run call in background and wait for finishing
env $env $solver_cmd $filename &
#alternative approach
#(export $env; $solver_cmd $filename) &
PID=$!
wait $PID
exit_code=$?
echo "Solver finished with exit code="$exit_code
exit $exit_code
