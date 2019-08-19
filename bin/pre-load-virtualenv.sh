#!/bin/bash

env

PYTHON_MAIN=${PYTHON_MAIN:-~/python}
echo "PYTHON_MAIN=${PYTHON_MAIN}"

#########################################################################
#### ---- Customization for multiple virtual python environment ---- ####
####      (most recommended approach and simple to switch venv)      ####
#########################################################################
PYTHON_VERSION=3
##PYTHON_VERSION=3.6
PYTHON_EXE=`which python${PYTHON_VERSION}`
VIRTUALENV_EXE=`which virtualenv`
VIRTUALENVWRAPPER_SHELL=`which virtualenvwrapper.sh`

export VIRTUALENVWRAPPER_PYTHON=${PYTHON_EXE}
export VIRTUALENVWRAPPER_VIRTUALENV=${VIRTUALENV_EXE}
source ${VIRTUALENVWRAPPER_SHELL}
export WORKON_HOME=${WORKON_HOME:-~/.virtualenvs}
if [ ! -d $WORKON_HOME ]; then
    mkdir -p $WORKON_HOME
fi

################################################################################
#### ---- Pre-load PIP modules for multiple virtual python environment ---- ####
################################################################################
#### ---- virtualenv setup ---- ####
for algorithm in `ls ${PYTHON_MAIN}`; do
    echo "============ Algorithm: ${algorithm} =============="
    ## ----------------------- ##
    ## -- virtualenvwrapper -- ##
    ## ----------------------- ##
    VENV_DIR=$(basename ${algorithm})
    mkvirtualenv -p ${PYTHON_EXE} ${VENV_DIR}
    workon ${VENV_DIR}
    ## PIP install requiremented packages
    if  [ -f ${PYTHON_MAIN}/${algorithm}/requirements.txt ]; then
        pip3 install -r ${PYTHON_MAIN}/${algorithm}/requirements.txt
    fi
done
