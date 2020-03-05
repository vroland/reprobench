#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
function interrupted(){
  kill -TERM $PID
}
trap interrupted TERM
trap interrupted INT

#
echo "Activating Conda environment"
if [ -d "$HOME/miniconda3/" ]; then
  source ~/miniconda3/etc/profile.d/conda.sh
elif [ -d "$HOME/anaconda3/" ]; then
  source ~/anaconda3/etc/profile.d/conda.sh
else
  echo "REQUIRES CONDA"
  exit 5
fi
conda activate rb

#cd "$(dirname "$0")" || (echo "Could not change directory to $0. Exiting..."; exit 1)
env="VOID=1"
solver_cmd="$HOME/src/frasmt/bin/fhtd $*"

echo
echo "env $env $solver_cmd"
echo


#NOTE: if you need to redirect the solver output in the future, we suggest to use stdlog.txt
#
# run call in background and wait for finishing
env $env $solver_cmd &
#alternative approach
#(export $env; $solver_cmd $filename) &
PID=$!
wait $PID
exit_code=$?
echo "Solver finished with exit code="$exit_code
exit $exit_code
