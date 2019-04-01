# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# We run a multi-stage Dockerfile which can generate --target (dev or prod)
# following https://blog.mikesir87.io/2018/07/leveraging-multi-stage-builds-single-dockerfile-dev-prod/

FROM jupyter/minimal-notebook as dev

LABEL maintainer="Jupyter Project <jupyter@googlegroups.com>"

USER root

# ffmpeg for matplotlib anim
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


USER $NB_UID

# Install Python 3 packages
# Remove pyqt and qt pulled in for matplotlib since we're only ever going to
# use notebook-friendly backends in these images
RUN conda install --quiet --yes \
    'conda-forge::blas=*=openblas' \
    'ipywidgets=7.4*' \
    'pandas=0.24*' \
    'numexpr=2.6*' \
    'matplotlib=3.0*' \
    'scipy=1.2*' \
    'seaborn=0.9*' \
    'scikit-learn=0.20*' \
    'scikit-image=0.14*' \
    'sympy=1.3*' \
    'cython=0.29*' \
    'patsy=0.5*' \
    'statsmodels=0.9*' \
    'cloudpickle=0.8*' \
    'dill=0.2*' \
    'dask=1.1.*' \
    'numba=0.42*' \
    'bokeh=1.0*' \
    'sqlalchemy=1.3*' \
    'hdf5=1.10*' \
    'h5py=2.9*' \
    'vincent=0.4.*' \
    'beautifulsoup4=4.7.*' \
    'protobuf=3.7.*' \
    'xlrd'  && \
    conda remove --quiet --yes --force qt pyqt && \
    conda clean -tipsy && \
    # Activate ipywidgets extension in the environment that runs the notebook server
    jupyter nbextension enable --py widgetsnbextension --sys-prefix

    # Also activate ipywidgets extension for JupyterLab
    # Check this URL for most recent compatibilities
    # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@^0.38 && \
    jupyter labextension install jupyterlab_bokeh@0.6.3 && \
    npm cache clean --force && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    rm -rf /home/$NB_USER/.node-gyp && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER


# Install facets which does not have a pip or conda package at the moment
RUN cd /tmp && \
    git clone https://github.com/PAIR-code/facets.git && \
    cd facets && \
    jupyter nbextension install facets-dist/ --sys-prefix && \
    cd && \
    rm -rf /tmp/facets && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" && \
fix-permissions /home/$NB_USER

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

WORKDIR /praetorian-tools/azure_cils_scanner

From dev as prod
RUN pip install azure_cis_scanner

# In development mode, it may be preferable to symlink these to make changes to repo.
COPY azure_cis_scanner/azure_cis_scanner.ipynb /home/jovyan/work/
COPY azure_cis_scanner/utils.py /home/jovyan/work

USER $NB_UID

