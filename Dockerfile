# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# We run a multi-stage Dockerfile which can generate --target (dev or prod)
# following https://blog.mikesir87.io/2018/07/leveraging-multi-stage-builds-single-dockerfile-dev-prod/

FROM jupyter/scipy-notebook:2ce7c06a61a1 as dev

LABEL scanner_maintainer="Praetorian <it@praetorian.com>"

USER root

RUN apt-get update && \
    apt-get install -y gnupg && \
    apt-get install -y curl

RUN echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ bionic main" | \
     tee /etc/apt/sources.list.d/azure-cli.list && \
    curl -L https://packages.microsoft.com/keys/microsoft.asc | apt-key add - 

RUN apt-get install apt-transport-https && \
    apt-get update && apt-get install -y azure-cli 
RUN apt-get install -y jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# In development mode, create these symlinks to make changes to repo.
# ln -s /praetorian-tools/azure_cis_scanner/azure_cis_scanner.ipynb /home/jovyan/work/
# ln -s /praetorian-tools/azure_cis_scanner/utils.py /home/jovyan/work

COPY requirements.txt .
RUN pip install -r requirements.txt

# Acutally install azscanner for production
# build base container:
# docker build -t azscan-dev --target dev .
# build prod container:
# docker build -t azscan-prod --target prod .

WORKDIR /praetorian-tools/azure_cis_scanner

From dev as prod
RUN pip install azure_cis_scanner

# In development mode, it may be preferable to symlink these to make changes to repo.
COPY azure_cis_scanner/azure_cis_scanner.ipynb /home/jovyan/work/
COPY azure_cis_scanner/utils.py /home/jovyan/work

USER $NB_UID

