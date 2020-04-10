#!/usr/bin/env python3
import glob
import json
import os

err_patterns = {"User time (seconds):": "cpu_time",
                "System time (seconds):": "cpu_sys_time",
                "Elapsed (wall clock) time (h:mm:ss or m:ss):": "wall_time",
                "Maximum resident set size (kbytes):": "max_memory",
                "Exit status:": "runsolver_STATUS"
                }

std_patterns = {"Exit code=": "return_code"}

folder = "./output_sparc"


def extract_data(stream, d, delimn, patterns):
    for line in stream.readlines():
        for p, k in patterns.items():
            n = line.find(p)
            if n != -1:
                m = line.rfind(delimn)
                if m == -1:
                    continue
                if delimn == ":":
                    d[k] = float(line[m + 2:])
                elif delimn == "=":
                    d[k] = float(line[m+1:])
                else:
                    raise NotImplementedError


for file in glob.glob('%s/**/stdout.txt' % folder, recursive=True):
    dirname = os.path.dirname(file)
    d = {"run_id": dirname, "wall_time": "nan", "cpu_sys_time": "nan", "cpu_time": "nan",
         "platform": "NetBSD 9.0-sparc", "hostname": "NetraX1", "verdict": "RTE", "return_code": 64,
         "runsolver_STATUS": 64, "runsolver_TIMEOUT": 0, "runsolver_MEMOUT": 0, "max_memory": "nan"}
    with open(file, 'r') as stdout_p:
        extract_data(stream=stdout_p, d=d, delimn="=", patterns=std_patterns)
    with open(f"{file[:-7]}err.txt", 'r') as stderr_p:
        extract_data(stream=stderr_p, d=d, delimn=":", patterns=err_patterns)

    d['wall_time'] = d["cpu_sys_time"] + d["cpu_time"]

    if d['return_code'] in (10, 20):
        d["verdict"] = "OK"
    elif d['return_code'] == 9:
        d["verdict"] = "TLE"
    else:
        print(d)
        raise NotImplementedError
        #TODO:
        # MEMOUT = "MEM"
        # RUNTIME_ERR = "RTE"
        # OUTPUT_LIMIT = "OLE"


    with open(f"{dirname}/result.json", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=4)
