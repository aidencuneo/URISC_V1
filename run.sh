#!/bin/bash

gcc src/urisc_v1.c -o bin/urisc_v1
if [[ $? != 0 ]]; then exit; fi
bin/urisc_v1 $@
