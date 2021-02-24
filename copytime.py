import sys
import re
import json
from collections import defaultdict

out = defaultdict(dict)

time_multipliers = {
    "s": 1.0,
    "ms": 0.001,
    "us": 10**-6,
    "ns": 10**-9,
}

def time_to_seconds(s):
    for unit in sorted(time_multipliers.keys(), key=lambda u: -len(u)):
        if s.endswith(unit):
            return float(s[:-len(unit)]) * time_multipliers[unit]
    raise ValueError("Unknown unit: " + s)

for path in sys.stdin.readlines():
    solver, instance = re.match("^./number_sat/default\[s=([A-Za-z_]*),t=0\]/mcc2020/(.*)/0/stderr.txt$", path.strip(), flags=re.MULTILINE).groups()
    with open(path.strip()) as f:
        content = f.read()
        times = {}
        for result in re.findall("^\s*[GPU activities:]*\s*([0-9.]+)%\s*([0-9.]+[a-z]+)\s*([0-9.]+)\s*([0-9.]+[a-z]+)\s*([0-9.]+[a-z]+)\s*([0-9.]+[a-z]+)\s*\[CUDA memcpy ([A-Za-z]+)\]$", content, re.MULTILINE):
            perc, time, calls, avg, t_min, t_max, direction = result
            time = time_to_seconds(time)
            calls = int(calls)
            avg = time_to_seconds(avg)
            t_min = time_to_seconds(t_min)
            t_max = time_to_seconds(t_max)
            times[direction] = {
                "percentage": float(perc),
                "time": time,
                "calls": calls,
                "avg": avg,
                "t_min": t_min,
                "t_max": t_max
            }

        out[solver][instance] = times

print(json.dumps(out))
