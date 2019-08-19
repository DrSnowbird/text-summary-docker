#!/bin/bash -x
set -e
env

PYTHON_MAIN=${PYTHON_MAIN:-~/python}
PYTHON_DATA=${PYTHON_DATA:-~/data}
echo "PYTHON_MAIN=${PYTHON_MAIN}"
echo "PYTHON_DATA=${PYTHON_DATA}"

#### ---- whether to automatically run algorithms for all the test data in ~/data folder ---- ####
RUN_ALGORITHM=${RUN_ALGORITHM:-0}

################################################
#### ---- Docker Entry Processing Here ---- ####
################################################
if [ $# -gt 0 ]; then
    #### ---- Use user-provided specific data files---- ####
    echo "Input command and arguments for Python to run: $@"
    exec "$@"
else
    echo "PYTHON_DATA=${PYTHON_DATA}"
    data_files=`ls ${PYTHON_DATA}`

    OUT_DIR=$HOME/workspace/textsummary
    mkdir -p ${OUT_DIR}

    if [ ${RUN_ALGORITHM} -gt 1 ]; then
        for algorithm in `ls ${PYTHON_MAIN}`; do
            cd ${algorithm}
            workon ${algorithm}
            for program in `ls *.py`; do
                echo "-------------- Python: ${program} -------------"
                echo "Running Summarizer Python main: ${program}"
                for data in ${data_files}; do
                    echo "............ Datafile: ${data} .............."
                    echo "... Summarizing data file: ${data}"
                    /usr/bin/python3 ${program} -d ${data} | tee ${OUT_DIR}/$(basename ${algorithm})_${program%.py}_$(basename ${data}).out
                done
            done
            cd ${PYTHON_MAIN}
        done
    fi
fi
