#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
#verbose=0
thp=0
opts=""
while getopts ":h?vt:s:f:i:" opt; do
    case "$opt" in
    h)
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
    *)
        opts="${opts} -$OPTARG"
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

solver_cmd="./${solver} ${opts} $*"

echo "Original input instance was $original_input"
echo "env $env $solver_cmd  $filename"
echo
echo


#NOTE: if you need to redirect the solver output in the future, we suggest to use stdlog.txt
#
# run call in background and wait for finishing
if [ "$solver" == "tuw_cpp_glibc" ] ; then
  env $env $solver_cmd $filename &
elif [ "$solver" == "scipjack_upstream" ] ; then
  env $env $solver_cmd -f $filename &
elif [ "$solver" == "hsv" ] ; then
#<prog> -solve_graphic <instance.stp> <?time_limit (seconds)>  <?enable_prune> <?enable_future_cost>
  env $env $solver_cmd -solve_graphic $filename 3600 1 1 &
else
  env $env $solver_cmd < $filename &
fi
#alternative approach
#(export $env; $solver_cmd $filename) &
PID=$!
wait $PID
exit_code=$?
echo "Solver finished with exit code="$exit_code
exit $exit_code
