from jupyter-scipy-azurecli-alpine:working

##########################################################
# The attempts
##########################################################

# Base container
# We originally tried nbgallery/jupyter-notebook but it was lacking pandas, matplotlib and numpy and
# pshchelo/alpine-jupyter-sci-py3 was already complete and smaller.

# We also looked at jupyter and continuum (anaconda) official images, but they were either not
# alpine based or had other issues.

# Once we started using pshchelo/alpine-jupyter-sci-py3 his should have worked
# git clone github.com/microsoft/azure-cli && cd azure-cli
# Use their Dockerfile, but start with `from pshchelo/alpine-jupyter-sci-py3`

# BUT there are lots of python versions floating around in pshchelo/alpine-jupyter-sci-py3 (conclicts)
# and the azure command completion totally borked things

# I next tried the azure-cli script install and after a few tries had it almost working
# curl -L https://aka.ms/InstallAzureCli | bash
# However, the script has no way to run install in silent/unattended mode.

##########################################################################################
# The hack that worked to build the base container jupyter-scipy-azurecli-alpine:working
##########################################################################################

# docker exec -it <container-id-for-pshchelo/alpine-jupyter-sci-py3> bash
# // handling the prompts manually
# curl -L https://aka.ms/InstallAzureCli | bash
# // Outside of the container
# docker commit <container-id-for-pshchelo/alpine-jupyter-sci-py3> jupyter-scipy-azurecli-alpine:working

##############################################################
# Now we can build our azure-cis-scanner-apline:working
##############################################################

COPY ./ /praetorian-tools/azure_cis_scanner/

RUN apk add terraform
# jupyter notebook runs with python3
RUN pip3 install -r /praetorian-tools/azure_cis_scanner/requirements.txt

SHELL ["/bin/bash", "-c"]
RUN source '/root/.bashrc'
RUN ln -s /root/bin/az /bin/az
RUN ln -s /praetorian-tools/azure_cis_scanner /notebooks/azure_cis_scanner

WORKDIR /notebooks

# To avoid shell terminal line overwrite weirdness
# https://stackoverflow.com/questions/38786615/docker-number-of-lines-in-terminal-changing-inside-docker/49281526#49281526
ENTRYPOINT [ "/bin/bash", "-l", "-i", "-c" ]
