#!/usr/bin/env bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
verbose=0

while getopts "h?vf:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=1
        ;;
    esac
done

shift $((OPTIND-1))

trap 'kill -TERM $PID' TERM

cmd="./gringo "$@" | ./clasp"
echo $cmd

cd "$(dirname "$0")"
bash -c "$cmd" &
PID=$!
wait $PID
exit $?
