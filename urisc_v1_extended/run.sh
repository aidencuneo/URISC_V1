#!/bin/bash

python3 urisc_v1_extended_v2.py $1
if [[ $? != 0 ]]; then exit; fi

python3 urisc_v1_extended.py "$1.xv1"
if [[ $? != 0 ]]; then exit; fi

../bin/urisc_v1 "$1.xv1.urisc_v1" -V
