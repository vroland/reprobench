#!env python3
import sys

num_verts = 0
num_edges = 0

with open(sys.argv[1]) as f:
    for line in f.readlines():
        l = line.strip().split(" ")
        if l[0] == "c":
            print("c", " ".join(l))
        elif l[0] == "p":
            num_verts = int(l[2])
        elif l[0] == "s":
            continue
        else:
            hyperedge = [abs(int(v)) for v in l if v.strip() != "0"]
            if len(hyperedge) <= 1:
                continue

            num_edges += len(hyperedge)*(len(hyperedge) - 1) // 2

print("p tw", num_verts, num_edges)

with open(sys.argv[1]) as f:
    for line in f.readlines():
        l = line.strip().split(" ")

        if l[0] not in ["c", "p", "s"]:
            hyperedge = [abs(int(v)) for v in l if v.strip() != "0"]
            if len(hyperedge) <= 1:
                continue

            for v1 in hyperedge:
                for v2 in hyperedge:
                    if v1 < v2:
                        print(v1, v2)

