#!/usr/bin/env python
""" file: run_tests.py (pysiss)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date: January 2015

    description: Build and run tests using an isolated conda environment.
        To set up, do
        `conda create -n pysiss-test python=2.7 pysiss gdal pytest`
"""

import subprocess
import textwrap

def main():
    script = textwrap.dedent("""\
        source activate pysiss-test && \
        mkdir -p logs && \
        NOW=`date +%d_%m_%Y_%H:%M:%S` && \
        LOGFILE=logs/test_$NOW.log && \
        echo Testing, output in $LOGFILE && \
        (py.test tests) > $LOGFILE && \
        source deactivate
    """)
    subprocess.call(script, shell=True, executable='/bin/bash')

if __name__ == '__main__':
    main()
