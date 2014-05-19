#!/usr/bin/env bash
# file:   built_all.sh
# author: Jess Robertson, CESRE
#         jesse.robertson@csiro.au
# date:   Thursday 2 May 2013
#
# description: Build a python package and documentation

# Generate stamps for logs
datestamp=`date +%F_%T`
build_log="logs/build_$datestamp"
test_log="logs/test_$datestamp"
mkdir -p logs
touch ${build_log}
touch ${test_log}

# # Uncomment to do delint
# echo " --> Pylinting..." | tee -a ${build_log} ${test_log}
# pylint pyboreholes --reports=n | tee -a ${build_log}
# # pylint pyboreholes --reports=y >> ${test_log}
# echo "" >> ${build_log}
# echo "" >> ${test_log}

# Clean
echo " --> Cleaning..." | tee -a ${build_log}
find . -name "*.pyc" -delete >> ${build_log}
rm -rf dist >> ${build_log}
rm -rf build >> ${build_log}
rm -rf *.egg-info >> ${build_log}
python setup.py clean >> ${build_log} 2>&1
echo "" >> ${build_log}

# Build
echo " --> Building..." | tee -a ${build_log}
python setup.py install --user >> ${build_log} 2>&1
echo "" >> ${build_log}

# Check test coverage if coverage.py is in path
path_to_coverage=$(which coverage)

# Run unittests
echo " --> Running unit tests..." | tee -a ${build_log} ${test_log}
echo "     Output in ${test_log}" | tee -a ${build_log}
if [[ -x "$path_to_coverage" ]] ; then
	coverage run --source=pyboreholes -m unittest tests >> ${test_log} 2>&1
else
	echo "" | tee -a ${test_log}
	echo " --> Couldn't find coverage.py on the current path" | tee -a ${test_log}
	echo "     Skipping code coverage tests" | tee -a ${test_log}
	echo "     To check test coverage, install coverage.py " | tee -a ${test_log}
	echo "         with 'pip install coverage'" | tee -a ${test_log}
	python -m unittest tests >> ${test_log} 2>&1
fi

# Check whether unittests passed
if [[ `cat ${test_log} | grep -c "FAILED"` -ne 0 ]]; then
    echo " --> WARNING: some tests failed! " \
        | tee -a ${build_log} ${test_log}
        
    # Uncomment to make Sublime Text open the file on test failure
	sublime_text ${test_log} &
else
    echo " --> All tests passed." | tee -a ${build_log} ${test_log}
fi

# Print unit test coverage report
if [[ -x "$path_to_coverage" ]] ; then
	echo "" >> ${test_log}
	echo "Test coverage:" >> ${test_log}
	echo "" >> ${test_log}
	coverage report >> ${test_log}
	echo "" >> ${test_log}
fi

# # Uncomment to make documentation
# echo " --> Making documentation..." | tee -a ${build_log}
# export PYTHONPATH=`pwd`/pyboreholes/:${PYTHONPATH}
# cd docs
# echo "     --> Cleaning documentation..." | tee -a ../${build_log}
# make clean >> ../${build_log}
# echo "     --> Building documentation..." | tee -a ../${build_log}
# echo "         Point your browser to docs/build/html/index.html" \
#     | tee -a ../${build_log}
# echo "     --> Building documentation..." >> ../${build_log}
# make html >> ../${build_log} 2>&1
# cd ..
