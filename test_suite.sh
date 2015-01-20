#!/usr/bin/env bash
# Build and run tests using py.test
# For use with Sublime Text build system

mkdir -p logs
NOW=`date +%d_%m_%Y_%H:%S`
LOGFILE=logs/test_$NOW.log
echo Testing, output in $LOGFILE
(py.test -n 4 tests) > $LOGFILE