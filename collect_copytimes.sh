set -e

cd output
find -name "stderr.txt" > err_files
python3 ../copytime.py < err_files > copytimes.json
