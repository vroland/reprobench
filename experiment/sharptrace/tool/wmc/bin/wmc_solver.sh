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
  solver_cmd="./d4 -mc $*"
elif [ "$solver" == "ganak" ] ; then
  solver_cmd="./ganak_glibc -p $*"
elif [ "$solver" == "minic2d" ] ; then
  solver_cmd="./minic2d_glibc -C $* -c"

elif [ "$solver" == "sharpsat" ] ; then
  solver_cmd="./sharpsat_glibc $*"
elif [ "$solver" == "sharpsat_trace" ] ; then
  solver_cmd="./sharpsat_trace.sh $*"

elif [ "$solver" == "tw_flowcutter" ] ; then
  solver_cmd="bash ./twgen.sh ./flow_cutter_pace17 "
elif [ "$solver" == "tw_tamaki" ] ; then
  solver_cmd="bash ./twgen.sh ./tw-heuristic "
elif [ "$solver" == "tw_htd" ] ; then
  solver_cmd="bash ./twgen.sh ./htd_main --opt width --output width --print-progress --iterations 0 "

elif [ "$solver" == "gpusat_cuda_td" ] ; then
  instfile=$(sed '1q;d' ~/reprobench/$original_input);
  decomposition=$(sed '2q;d' ~/reprobench/$original_input);  
  filename=""

  newfile="/tmp/$(basename $original_input).cnf"
  echo "using instfile: $instfile decomposition: $decomposition"

  bzcat $instfile > $newfile 
  solver_cmd="./gpusat_cuda -f $newfile -d $decomposition"

elif [ "$solver" == "gpusat_cuda_td2" ] ; then
  solver_cmd="./gpusat_cuda -d $HOME/reprobench/$original_input.td -f $*"
elif [ "$solver" == "gpusat_td2" ] ; then
  solver_cmd="./gpusat -d $HOME/reprobench/$original_input.td -f $*"

else
  solver_cmd="./"$solver"_glibc $*"
fi


>&2 echo "Original input instance was $original_input"
>&2 echo "env $env $solver_cmd $filename"
>&2 echo
>&2 echo

#NOTE: if you need to redirect the solver output in the future, we suggest to use stdlog.txt
#
# run call in background and wait for finishing
env $env $solver_cmd $filename &
#alternative approach
#(export $env; $solver_cmd $filename) &
PID=$!
wait $PID
exit_code=$?
>&2 echo "Solver finished with exit code="$exit_code
>&2 exit $exit_code
