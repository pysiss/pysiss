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

echo " --> Pylinting..." | tee -a ${build_log} ${test_log}
pylint python_boreholes --reports=n | tee -a ${build_log}
# pylint borehole_analysis --reports=y >> ${test_log}
echo "" >> ${build_log}
echo "" >> ${test_log}

echo " --> Cleaning..." | tee -a ${build_log}
python setup.py clean >> ${build_log}
echo "" >> ${build_log}

echo " --> Building..." | tee -a ${build_log}
python setup.py build >> ${build_log}
sudo python setup.py install >> ${build_log}
echo "" >> ${build_log}

echo " --> Running unit tests..." | tee -a ${build_log} ${test_log}
echo "     Output in ${test_log}" | tee -a ${build_log}
python -m unittest tests >> ${test_log} 2>&1
if [[ `tail -n 5 ${test_log} | grep -c FAILED` -ne 0 ]]; then
    echo "     WARNING: some tests failed! " \
        | tee -a ${build_log} ${test_log}
else
    echo "     All tests passed." | tee -a ${build_log} ${test_log}
fi
echo "" >> ${build_log}

# # Make documentation
# echo " --> Making documentation..." | tee -a ${build_log}
# export PYTHONPATH=`pwd`/borehole_analysis/:${PYTHONPATH}
# cd docs
# echo "     --> Cleaning documentation..." | tee -a ../${build_log}
# make clean >> ../${build_log}
# echo "     --> Building documentation..." | tee -a ../${build_log}
# echo "         Point your browser to docs/build/html/index.html" \
#     | tee -a ../${build_log}
# echo "     --> Building documentation..." >> ../${build_log}
# make html >> ../${build_log} 2>&1
# cd ..