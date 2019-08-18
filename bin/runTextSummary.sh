#!/bin/bash -x

env

PYTHON_MAIN=${PYTHON_MAIN:-~/python}
PYTHON_DATA=${PYTHON_DATA:-~/data}
echo "PYTHON_MAIN=${PYTHON_MAIN}"
echo "PYTHON_DATA=${PYTHON_DATA}"

#########################################################################
#### ---- Customization for multiple virtual python environment ---- ####
####      (most recommended approach and simple to switch venv)      ####
#########################################################################
PYTHON_VERSION=3
#PYTHON_VERSION=3.6
PYTHON_EXE=`which python${PYTHON_VERSION}`
VIRTUALENV_EXE=`which virtualenv`
VIRTUALENVWRAPPER_SHELL=`which virtualenvwrapper.sh`

export VIRTUALENVWRAPPER_PYTHON=${PYTHON_EXE}
export VIRTUALENVWRAPPER_VIRTUALENV=${VIRTUALENV_EXE}
source ${VIRTUALENVWRAPPER_SHELL}
export WORKON_HOME=${WORKON_HOME:-~/Envs}
if [ ! -d $WORKON_HOME ]; then
    mkdir -p $WORKON_HOME
fi

echo "PYTHON_DATA=${PYTHON_DATA}"
data_files=`ls ${PYTHON_DATA}`

OUT_DIR=$HOME/workspace/textsummary
mkdir -p ${OUT_DIR}

#### ---- virtualenv setup ---- ####
cd ${PYTHON_MAIN}
#for algorithm in `ls ${PYTHON_MAIN}`; do
for algorithm in "text-summary-with-PageRank"; do

    cd ${algorithm}
    echo "============ Algorithm: ${algorithm} =============="
    ## ----------------------- ##
    ## -- virtualenvwrapper -- ##
    ## ----------------------- ##
    deactivate
    VENV_DIR=$(basename ${algorithm})
    mkvirtualenv ${VENV_DIR}
    workon ${VENV_DIR}
    ## PIP install requiremented packages
    if  [ -f ./requirements.txt ]; then
        pip3 install -r ./requirements.txt
    fi
    for program in `ls *.py`; do
        echo "-------------- Python: ${program} -------------"
        echo "Running Summarizer Python main: ${program}"
        for data in ${data_files}; do
            echo "............ Datafile: ${data} .............."
            echo "... Summarizing data file: ${data}"
            /usr/bin/python3 ${program} -d ${data} | tee ${OUT_DIR}/$(basename ${algorithm})_${program%.py}_$(basename ${data}).out
        done
    done
done
