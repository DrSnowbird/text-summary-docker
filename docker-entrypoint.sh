#!/bin/bash
set -e
env

echo "PYTHON_MAIN=${PYTHON_MAIN}"

if [ $# -gt 0 ]; then
    #### ---- Use user-provided specific data files---- ####
    echo "Input command and arguments for Python to run: $@"
    exec "$@"
else
    echo "PYTHON_DATA=${PYTHON_DATA}"
    data_files=`ls $PYTHON_DATA`

    set -x
    pip install -r ${PYTHON_MAIN}/requirements.txt
    for program in `ls $PYTHON_MAIN/*.py`; do
        echo "=================================="
        echo "... Running Summarizer Python main: $program"
        for data in $data_files; do
            echo "----------------------------------"
            echo "... Summarizing data file: ${data}"
            /usr/bin/python3 ${program} -d ${data}
        done
    done
fi