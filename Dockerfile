FROM openkbs/jdk-mvn-py3

MAINTAINER OpenKBS <DrSnowbird@openkbs.org>

USER ${USER}
WORKDIR ${HOME}

# ###################################
# #### ----   PIP modules: ----  ####
# ###################################
COPY requirements.txt ./
RUN sudo -H pip3 --no-cache-dir install --ignore-installed -U -r requirements.txt

##################################
#### Set up user environments ####
##################################
RUN echo "USER =======> ${USER}"

ENV WORKSPACE=${HOME}/workspace
RUN mkdir -p ${WORKSPACE} 

ARG PYTHON_MAIN=${PYTHON_MAIN:-"$HOME/python"}
ARG PYTHON_DATA=${PYTHON_DATA:-"$HOME/data"}

ENV PYTHON_MAIN=${PYTHON_MAIN}
ENV PYTHON_DATA=${PYTHON_DATA}

VOLUME ${PYTHON_MAIN}
VOLUME ${PYTHON_DATA}
#RUN mkdir ${PYTHON_MAIN} ${PYTHON_DATA}

COPY ./python/* ${PYTHON_MAIN}/
COPY ./data/* ${PYTHON_DATA}/
COPY ./bin $HOME/
COPY ./docker-entrypoint.sh $HOME/
RUN sudo chmod +x $HOME/docker-entrypoint.sh

WORKDIR "$HOME/data"
ENTRYPOINT ["/home/developer/docker-entrypoint.sh"]

CMD ["/bin/bash"]
