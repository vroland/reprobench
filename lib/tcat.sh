#!/usr/bin/env bash
# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

while getopts "h?f:o:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    f)  filename=$OPTARG
        ;;
    o)  output=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

function cleanup(){
  if [[ $temp == /dev/shm/tmp.* ]] ; then
    rm -r $temp
  fi
  echo "========================================================="
  echo "Deleted temp working directory $temp"
  echo "========================================================="
}

if [ -z $filename ] ; then
  echo 'Missing filename. Exiting...'
  exit 1
fi

if [ -z $output ] ; then
  temp=$(mktemp -d -p /dev/shm -t tmp.$(basename $0).XXXXXXXXX)
  echo "Created temp working directory $temp"
  trap cleanup EXIT
  output=$temp/$(basename $filename)
fi



type=$(file -b --mime-type $filename)
echo $type

if [ $type == "application/x-lzma" ] ; then
  prep_cmd="lzcat $filename"
elif [ $type == "application/x-bzip2" ] ; then
  prep_cmd="bzcat $filename"
elif [ $type == "application/x-xz" ] ; then
  prep_cmd="xzcat $filename"
else
  prep_cmd="zcat -f $filename"
fi

echo "Preparing instance in $output"
echo "$prep_cmd > $output"
$prep_cmd > $output

