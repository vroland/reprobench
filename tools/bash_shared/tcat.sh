#!/usr/bin/env bash
#TODO: use slurm provided temp
temp=$(mktemp -d -p /dev/shm -t tmp.$(basename $0).XXXXXXXXX)
echo "Created temp working directory $temp"

#template does not support curly brackets
function cleanup(){
  if [[ $temp == /dev/shm/tmp.* ]] ; then
    rm -r $temp
  fi
  echo "========================================================="
  echo "Deleted temp working directory $temp"
  echo "========================================================="
}
trap cleanup EXIT


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

decomp_filename=$temp/$(basename $filename)
echo "Preparing instance in /dev/shm..."
echo "$prep_cmd > $decomp_filename"
$prep_cmd > $decomp_filename

