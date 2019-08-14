FROM openkbs/jdk-mvn-py3

MAINTAINER OpenKBS <DrSnowbird@openkbs.org>

USER ${USER}
WORKDIR ${HOME}

###################################
#### ----   PIP modules: ----  ####
###################################
COPY requirements.txt ./
RUN sudo -H pip3 --no-cache-dir install --ignore-installed -U -r requirements.txt

##################################################################################
#### ---- Dowload NLTK Corpora stopwords.zip package to avoid networking ---- ####
##################################################################################
#### ref: http://www.nltk.org/nltk_data/
#### ref: https://medium.com/@satorulogic/how-to-manually-download-a-nltk-corpus-f01569861da9

ARG NLTK_STOPWORDS_PATH=$HOME/nltk_data/corpora
ARG NLTK_STOPWORDS_ZIP=https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip
RUN mkdir -p ${NLTK_STOPWORDS_PATH} ; cd ${NLTK_STOPWORDS_PATH}; wget -c ${NLTK_STOPWORDS_ZIP}; unzip $(basename ${NLTK_STOPWORDS_ZIP})

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

COPY ./python/* ${PYTHON_MAIN}/
COPY ./data/* ${PYTHON_DATA}/
COPY ./bin $HOME/
COPY ./docker-entrypoint.sh $HOME/
RUN sudo chmod +x $HOME/docker-entrypoint.sh

WORKDIR "$HOME/data"
ENTRYPOINT ["/home/developer/docker-entrypoint.sh"]

#CMD ["/bin/bash"]
