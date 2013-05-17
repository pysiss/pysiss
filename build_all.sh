#!/usr/bin/env bash
# file:   built_all.sh
# author: Jess Robertson, CESRE
#         jesse.robertson@csiro.au
# date:   Thursday 2 May 2013
#
# description: Build python package and documentation
datestamp=`date +%F_%T`
build_log="logs/build_$datestamp"
test_log="logs/test_$datestamp"
mkdir -p logs
touch ${build_log}
touch ${test_log}

echo " --> Pylinting..."
echo ""
echo " --> Pylinting..." >> ${build_log}
echo "" >> ${build_log}
pylint borehole_analysis --reports=n
pylint borehole_analysis --reports=y >> ${build_log}
echo "" >> ${build_log}
echo ""

echo " --> Cleaning..."
echo " --> Cleaning..." >> ${build_log}
python setup.py clean >> ${build_log}
echo "" >> ${build_log}

echo " --> Building..."
echo " --> Building..." >> ${build_log}
python setup.py build >> ${build_log}
sudo python setup.py install >> ${build_log}
echo "" >> ${build_log}

echo " --> Running unit tests..."
echo "     Output in ${test_log}"
echo " --> Running unit tests..." >> ${build_log}
echo "     Output in ${test_log}" >> ${build_log}
echo "" >> ${build_log}
python -m unittest tests 2> ${test_log}
echo "" >> ${build_log}
echo ""

# # Make documentation
# echo " --> Making documentation..."
# echo " --> Making documentation..." >> ${build_log}
# export PYTHONPATH=`pwd`/borehole_analysis/:${PYTHONPATH}
# cd docs
# echo "     --> Cleaning documentation..."
# echo "     --> Cleaning documentation..." >> ../${build_log}
# make clean >> ../${build_log}
# echo "     --> Building documentation..."
# echo "         Point your browser to docs/build/html/index.html"
# echo "     --> Building documentation..." >> ../${build_log}
# make html >> ../${build_log} 2>&1
# cd ..