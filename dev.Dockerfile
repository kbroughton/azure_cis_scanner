# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# We run a multi-stage Dockerfile which can generate --target (dev or prod)
# following https://blog.mikesir87.io/2018/07/leveraging-multi-stage-builds-single-dockerfile-dev-prod/

FROM jupyter/scipy-notebook:dc9744740e12 as dev
LABEL scanner_maintainer="kesten.broughton@praetorian.com, Praetorian <it@praetorian.com>"

USER root

RUN apt-get update && \
    apt-get install -y gnupg && \
    apt-get install -y curl

RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

RUN apt-get install apt-transport-https && \
    apt-get update && apt-get install -y azure-cli 
RUN apt-get install -y jq && \
    apt-get clean

COPY . /azure_cis_scanner
WORKDIR /azure_cis_scanner

RUN pip install -r requirements.txt

#RUN setup.py install --dev
RUN pip install -e .

