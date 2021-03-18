function interrupted(){
  kill -TERM $PID
}
trap interrupted TERM
trap interrupted INT

array=( $@ )
len=${#array[@]}
python3 ./cnf2pace.py "${@: -1}" | ${array[@]:0:$len-1} &
PID=$!
wait $PID
