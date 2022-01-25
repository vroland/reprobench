#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
#verbose=0
thp=0
while getopts "h?vt:f:i:p:o:" opt; do
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
    p)  preprocessor=$OPTARG
        ;;
    f)  filename=$OPTARG
        ;;
    i)  original_input=$OPTARG
        ;;
    o)  output=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

function interrupted(){
  kill -TERM $PID
}
trap interrupted TERM
trap interrupted INT


if [ -z $preprocessor ] ; then
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
else
  env=VOID=1
fi

cd "$(dirname "$0")" || (echo "Could not change directory to $0. Exiting..."; exit 1)

if [ $preprocessor == "pmc" ] ; then
  echo "Preserve number of solutions."
  solver_cmd="./"$preprocessor" -affine -orGate -equiv -vivification -litImplied -eliminateLit -addClause -rewrite $@"
elif [ $preprocessor == "pmcstar" ] ; then
  echo "Preserve models."
  solver_cmd="./pmc -vivification -eliminateLit -litImplied -iterate=10 $@"
  #-cpu-lim=5
elif [ $preprocessor == "b+e" ] ; then
  #-limSolver=1000
  solver_cmd="./"$preprocessor" $@"
else
  solver_cmd="./"$preprocessor" $@"
fi

echo "Original input instance was $original_input"
echo "env $env $solver_cmd $filename $output"
echo
echo

#NOTE: if you need to redirect the solver output in the future, we suggest to use stdlog.txt
#
# run call in background and wait for finishing
tmpfile=$(mktemp /dev/shm/$preprocessor.XXXXXX)
echo "Writing to $tmpfile."
env $env $solver_cmd $filename > $tmpfile &
#alternative approach
#(export $env; $solver_cmd $filename) &
PID=$!
wait $PID
exit_code=$?
echo "Preprocessor finished with exit code="$exit_code
echo $exit_code

if [ -s $tmpfile ] ; then
  echo "Non-empty output moving $tmpfile to $output"
  mv $tmpfile $output
else
  echo "Empty output in $tmpfile\n Removing the file..."
  rm $tmpfile
fi

exit $exit_code
