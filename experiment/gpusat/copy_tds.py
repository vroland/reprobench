import sys
import os
import re
import hashlib

hashes = set()
lines = 0

for l in sys.stdin.readlines():
    match = re.match(r"mcc_decompositions/default\[s=([A-Za-z0-9_]*),t=0\]/mcc2020/(.*)/([0-9]+)/decomposition.td", l)
    decomposer, instance, run = (match.group(1), match.group(2), match.group(3))
    paramfile = os.path.join("decomp_runs", f"{decomposer}_{instance}_{run}.params");
    path_prefix = os.path.abspath(os.path.dirname(__file__))
    with open(l.strip(), "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
        hashes.add(h)
    #if not instance in ["track1_131.mcc2020_cnf.bz2", "track1_134.mcc2020_cnf.bz2"]:
    #    continue

    with open(paramfile, "w") as f:
        f.write(os.path.join(path_prefix, f"track1_all/{instance}\n"))
        f.write(os.path.join(path_prefix, l))
    print (paramfile + ".params", decomposer, instance, run)
    lines += 1
print (len(hashes), lines)
