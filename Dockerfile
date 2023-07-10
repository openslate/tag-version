FROM python:3.6-stretch
LABEL maintainer="code@doubleverify.com"

# Install tag-version
ENV SRC_DIR /usr/local/src
WORKDIR ${SRC_DIR}

RUN mkdir ${SRC_DIR}/results

RUN pip3 install setuptools twine pylama pylint pylama-pylint pytest

COPY files/ /
RUN chmod +x /usr/local/bin/*

COPY ./ ${SRC_DIR}/

RUN python setup.py install

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
