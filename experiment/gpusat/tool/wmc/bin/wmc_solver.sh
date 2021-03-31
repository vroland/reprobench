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

elif [ "$solver" == "gpusat_array" ] ; then
  solver_cmd="./gpusat --dataStructure array -f $*"
elif [ "$solver" == "gpusat_tree" ] ; then
  solver_cmd="./gpusat --dataStructure tree -f $*"
elif [ "$solver" == "gpusat_cuda_array" ] ; then
  solver_cmd="./gpusat_cuda --dataStructure array -f $*"
elif [ "$solver" == "gpusat_cuda_tree" ] ; then
  solver_cmd="./gpusat_cuda --dataStructure tree -f $*"
elif [ "$solver" == "gpusat_cuda_array_unpinned" ] ; then
  solver_cmd="./gpusat_cuda --unpinned --dataStructure array -f $*"
elif [ "$solver" == "gpusat_cuda_tree_unpinned" ] ; then
  solver_cmd="./gpusat_cuda --unpinned --dataStructure tree -f $*"

elif [ "$solver" == "gsc_prof_tree_pin_cache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure tree -f $*"
elif [ "$solver" == "gsc_prof_tree_pin_nocache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure tree --no-cache -f $*"
elif [ "$solver" == "gsc_prof_tree_nopin_cache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure tree --unpinned -f $*"
elif [ "$solver" == "gsc_prof_tree_nopin_nocache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure tree --no-cache --unpinned -f $*"
elif [ "$solver" == "gsc_prof_array_pin_cache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure array -f $*"
elif [ "$solver" == "gsc_prof_array_pin_nocache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure array --no-cache -f $*"
elif [ "$solver" == "gsc_prof_array_nopin_cache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure array --unpinned -f $*"
elif [ "$solver" == "gsc_prof_array_nopin_nocache" ] ; then
  solver_cmd="nvprof ./gpusat_cuda --dataStructure array --no-cache --unpinned -f $*"

elif [ "$solver" == "gpusat_any" ] ; then
  solver_cmd="./gpusat -f $*"
elif [ "$solver" == "gpusat_cuda_any" ] ; then
  solver_cmd="./gpusat_cuda -f $*"
elif [ "$solver" == "gpusat_dp_any" ] ; then
  solver_cmd="./cuda_port -f $*"

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

elif [ "$solver" == "sharpsat_gpu" ] ; then
  solver_cmd="./sharpsat_gpu -gpu $*"
elif [ "$solver" == "sharpsat_gpu_prof" ] ; then
  solver_cmd="./sharpsat_gpu_prof -gpu $*"
elif [ "$solver" == "sharpsat_gpu_prof_nogpu" ] ; then
  solver_cmd="./sharpsat_gpu_prof $*"
elif [ "$solver" == "sharpsat_gpusat" ] ; then
  solver_cmd="./sharpsat_gpusat -gpu $*"
elif [ "$solver" == "sharpsat_gpusat_nogpu" ] ; then
  solver_cmd="./sharpsat_gpusat $*"
elif [ "$solver" == "sharpsat_gpusat_prof" ] ; then
  solver_cmd="./sharpsat_gpusat_prof -gpu $*"
elif [ "$solver" == "sharpsat_gpusat_prof_nogpu" ] ; then
  solver_cmd="./sharpsat_gpusat_prof $*"
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
