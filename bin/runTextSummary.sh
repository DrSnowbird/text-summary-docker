#!/bin/bash -x

env

echo "----- begin processing summarization for various algorithms -----"

PYTHON_MAIN=${PYTHON_MAIN:-~/python}
PYTHON_DATA=${PYTHON_DATA:-~/data}
echo "PYTHON_MAIN=${PYTHON_MAIN}"
echo "PYTHON_DATA=${PYTHON_DATA}"

OUT_DIR=$HOME/workspace/textsummary
mkdir -p ${OUT_DIR}

#### ---- virtualenv setup ---- ####
cd ${PYTHON_MAIN}

for algorithm in `ls ${PYTHON_MAIN}`; do
    _algorithm=$(basename ${algorithm})
    echo "============ Algorithm: ${algorithm} =============="
    ## ----------------------- ##
    ## -- virtualenvwrapper -- ##
    ## ----------------------- ##
    deactivate
    VENV_DIR=$(basename ${algorithm})
    workon ${VENV_DIR}
    for program in `ls ${PYTHON_MAIN}/${algorithm}/*.py`; do
        _program=$(basename ${program})
        echo "-------------- Python program: ${program} -------------"
        for data in `ls ${PYTHON_DATA}/*.txt`; do
            _data=$(basename ${data})
            echo "............ Datafile: ${data} .............."
            echo "... Summarizing data file: ${data}"
	    /usr/bin/python3 ${PYTHON_MAIN}/${_algorithm})/${_program}) -d ${PYTHON_DATA}/${_data}) | tee ${OUT_DIR}/${_algorithm})_${_program%.py}_${_data}).out
        done
    done
done
