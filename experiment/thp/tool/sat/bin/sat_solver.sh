#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
#verbose=0
thp=0
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
else
  env=VOID=1
fi

cd "$(dirname "$0")" || (echo "Could not change directory to $0. Exiting..."; exit 1)


if [ "$solver" == "plingeling" ] ; then
  solver_cmd="./"$solver"_glibc -t 1 -g 8 $*"
elif [ "$solver" == "lingelingplain" ] ; then
  solver_cmd="./lingeling_glibc --plain $*"
elif [ "$solver" == "zchaff.2001" ] ; then
  solver_cmd="./zchaff.2001 $*"
elif [ "$solver" == "zchaff.2004.05.13" ] ; then
  solver_cmd="./zchaff.2004.05.13 $*"
elif [ "$solver" == "zchaff.2004.11.15" ] ; then
  solver_cmd="./zchaff.2004.11.15 $*"
elif [ "$solver" == "zchaff.2007.03.12_x64" ] ; then
  solver_cmd="./zchaff.2007.03.12_x64 $*"
elif [ "$solver" == "grasp.1996_jkf_mh" ] ; then
  solver_cmd="./grasp.1996_jkf_mh $*"
elif [ "$solver" == "grasp.2008.06.22_armin1" ] ; then
  solver_cmd="./grasp.2008.06.22_armin1 $*"
elif [ "$solver" == "grasp.2008.06.22_armin2" ] ; then
  solver_cmd="./grasp.2008.06.22_armin2 $*"
elif [ "$solver" == "belsat" ] ; then
  solver_cmd="./belsat $*"
elif [ "$solver" == "minisat2.0" ] ; then
  solver_cmd="./minisat2.0 $*"
elif [ "$solver" == "rsat_2.0" ] ; then
  solver_cmd="./rsat_2.0 $*"
elif [ "$solver" == "siege_v1" ] ; then
  solver_cmd="./siege_v1 $*"
elif [ "$solver" == "siege_v3" ] ; then
  solver_cmd="./siege_v1 $*"
elif [ "$solver" == "siege_v4" ] ; then
  solver_cmd="./siege_v1 $*"
elif [ "$solver" == "ubcsat2006gsat" ] ; then
  solver_cmd="./ubcsat2006 $* -alg gsat -solve -i"
elif [ "$solver" == "ubcsat2006gsats" ] ; then
  solver_cmd="./ubcsat2006 $* -alg gsat -v simple -solve -i"
#elif [ "$solver" == "ubcsat2006gsatw" ] ; then
#  solver_cmd="./ubcsat2006 $* -alg gsat -w -solve -i"
elif [ "$solver" == "ubcsat2006gwsat" ] ; then
  solver_cmd="./ubcsat2006 $* -alg gwsat -solve -i"
#elif [ "$solver" == "ubcsat2006gwsatw" ] ; then
#  solver_cmd="./ubcsat2006 $* -alg gwsat -w -solve -i"
elif [ "$solver" == "ubcsat2006gsat-tabu" ] ; then
  solver_cmd="./ubcsat2006 $* -alg gsat-tabu -solve -i"
elif [ "$solver" == "ubcsat2006hsat" ] ; then
  solver_cmd="./ubcsat2006 $* -alg hsat -solve -i"
#elif [ "$solver" == "ubcsat2006hsatw" ] ; then
#  solver_cmd="./ubcsat2006 $* -alg hsat -w -solve -i"
elif [ "$solver" == "ubcsat2006hwsat" ] ; then
  solver_cmd="./ubcsat2006 $* -alg hwsat -solve -i"
#elif [ "$solver" == "ubcsat2006hwsatw" ] ; then
#  solver_cmd="./ubcsat2006 $* -alg hwsat -w -solve -i"
elif [ "$solver" == "ubcsat2006walksat" ] ; then
  solver_cmd="./ubcsat2006 $* -alg walksat -solve -i"
elif [ "$solver" == "ubcsat2006walksat-tabu" ] ; then
  solver_cmd="./ubcsat2006 $* -alg walksat-tabu -solve -i"
elif [ "$solver" == "ubcsat2006novelty" ] ; then
  solver_cmd="./ubcsat2006 $* -alg novelty -solve -i"
elif [ "$solver" == "ubcsat2006novelty+" ] ; then
  solver_cmd="./ubcsat2006 $* -alg novelty+ -solve -i"
elif [ "$solver" == "ubcsat2006novelty++" ] ; then
  solver_cmd="./ubcsat2006 $* -alg novelty++ -solve -i"
elif [ "$solver" == "ubcsat2006adaptnovelty+" ] ; then
  solver_cmd="./ubcsat2006 $* -alg adaptnovelty+ -solve -i"
elif [ "$solver" == "ubcsat2006rnovelty" ] ; then
  solver_cmd="./ubcsat2006 $* -alg rnovelty -solve -i"
elif [ "$solver" == "ubcsat2006rnovelty+" ] ; then
  solver_cmd="./ubcsat2006 $* -alg rnovelty+ -solve -i"
elif [ "$solver" == "ubcsat2006saps" ] ; then
  solver_cmd="./ubcsat2006 $* -alg saps -solve -i"
elif [ "$solver" == "ubcsat2006rsaps" ] ; then
  solver_cmd="./ubcsat2006 $* -alg rsaps -solve -i"
elif [ "$solver" == "ubcsat2006sapsnr" ] ; then
  solver_cmd="./ubcsat2006 $* -alg sapsnr -solve -i"
elif [ "$solver" == "ubcsat2006paws" ] ; then
  solver_cmd="./ubcsat2006 $* -alg paws -solve -i"
elif [ "$solver" == "ubcsat2006ddfw" ] ; then
  solver_cmd="./ubcsat2006 $* -alg ddfw -solve -i"
elif [ "$solver" == "ubcsat2006g2wsat" ] ; then
  solver_cmd="./ubcsat2006 $* -alg g2wsat -solve -i"
elif [ "$solver" == "ubcsat2006rots" ] ; then
  solver_cmd="./ubcsat2006 $* -alg rots -solve -i"
elif [ "$solver" == "ubcsat2006irots" ] ; then
  solver_cmd="./ubcsat2006 $* -alg irots -solve -i"
elif [ "$solver" == "ubcsat2006samd" ] ; then
  solver_cmd="./ubcsat2006 $* -alg samd -solve -i"
elif [ "$solver" == "ubcsat2006urwalk" ] ; then
  solver_cmd="./ubcsat2006 $* -alg urwalk -solve -i"
elif [ "$solver" == "ubcsat2006crwalk" ] ; then
  solver_cmd="./ubcsat2006 $* -alg crwalk -solve -i"
else
  solver_cmd="./"$solver"_glibc $*"
fi

echo "Original input instance was $original_input"
echo "env $env $solver_cmd $filename"
echo
echo

echo "FILENAME:"$filename

if [ ! -z "$preprocessor" ] & [ "$preprocessor" != "none" ]; then
  tmpfile=$(mktemp /tmp/sat_preprocessed.XXXXXXXXX)
  trap "rm $tmpfile" EXIT
  if [ "$preprocessor" == "minisat2" ] ; then
    #experiment/thp/tool/sat/bin/minisat_glibc -pre -no-solve -dimacs=/tmp/foo
    pre_cmd="./minisat_glibc -pre -no-solve -dimacs=$tmpfile $filename"
  elif [ "$preprocessor" == "satelite" ] ; then
    echo "FIXME"
    exit 1
    pre_cmd="./satelite -pre -no-solve -dimacs=$tmpfile $filename"
  elif [ "$preprocessor" == "glucose" ] ; then
    pre_cmd="./glucose-4.2.1_glibc -pre  -dimacs=$tmpfile $filename"
  else
    echo "Preprocessor '$preprocessor' undefined. Exiting..."
    exit 5
  fi
  env $env $pre_cmd &
  PID=$!
  wait $PID
  filename=$tmpfile
fi


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
