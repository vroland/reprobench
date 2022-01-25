#!/usr/bin/env bash
./sharpsat_trace -noPP -proof $1 | gzip -c
