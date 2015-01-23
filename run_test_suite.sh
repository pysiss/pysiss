#!/usr/bin/env bash
# Build and run tests using an isolated conda environment
#
# To set up, do
#    conda create -n pysiss-test python=2.7 pysiss pytest

source ~/.anaconda/envs/pysiss-test/bin/activate
mkdir -p logs
NOW=`date +%d_%m_%Y_%H:%M:%S`
LOGFILE=logs/test_$NOW.log
echo Testing, output in $LOGFILE
(python setup.py test) > $LOGFILE
source deactivate