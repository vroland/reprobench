array=( $@ )
len=${#array[@]}
python3 ./cnf2pace.py "${@: -1}" | ${array[@]:0:$len-1}
