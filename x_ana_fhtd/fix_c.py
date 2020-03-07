#!/usr/bin/env python3

import os
import fnmatch

for root, dir, files in os.walk("output"):
    for fname in fnmatch.filter(files, "stdout.txt"):
        print(os.path.join(root,fname))
        with open(os.path.join(root,fname), 'r+') as f:
            lines = []
            for line in f.readlines():
                if not line.startswith('{') and not line.startswith('c '):
                    lines.append(f"c {line}")
                else:
                    lines.append(f"{line}")
            f.seek(0)
            f.write("".join(lines))
