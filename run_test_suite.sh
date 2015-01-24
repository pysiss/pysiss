#!/usr/bin/env bash
# Build and run tests using an isolated conda environment
#
# To set up, do
#    conda create -n pysiss-test python=2.7 pysiss gdal pytest

source activate pysiss-test
mkdir -p logs
NOW=`date +%d_%m_%Y_%H:%M:%S`
LOGFILE=logs/test_$NOW.log
echo Testing, output in $LOGFILE
(py.test tests) > $LOGFILE
source deactivate