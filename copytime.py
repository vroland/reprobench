import sys
import re
import json
from collections import defaultdict

out = defaultdict(dict)

for path in sys.stdin.readlines():
	solver, instance = re.match("^./number_sat/default\[s=([A-Za-z_]*),t=0\]/mcc2020/(.*)/0/stderr.txt$", path.strip(), flags=re.MULTILINE).groups()
	with open(path.strip()) as f:
		content = f.read()
		times = {}
		for result in re.findall("^\s*([0-9.]+)%\s*([0-9.]+[a-z]+)\s*([0-9.]+)\s*([0-9.]+[a-z]+)\s*([0-9.]+[a-z]+)\s*([0-9.]+[a-z]+)\s*\[CUDA memcpy ([A-Za-z]+)\]$", content, re.MULTILINE):	
			perc, time, calls, avg, t_min, t_max, direction = result
			times[direction] = float(perc)

		out[solver][instance] = times

print(json.dumps(out))
