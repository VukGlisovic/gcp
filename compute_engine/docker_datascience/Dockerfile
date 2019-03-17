# https://hub.docker.com/_/ubuntu/
FROM ubuntu:18.04

USER root

# Set password for root user
RUN echo "root:vukvukvuk" | chpasswd

# Install all OS dependencies for jupyter notebook server that starts (e.g. download as all possible file formats)
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -yq dist-upgrade && \
    apt-get install -yq --no-install-recommends \
    wget \
    curl \
    npm \
    bzip2 \
    ca-certificates \
    sudo \
    locales \
    fonts-liberation \
    nano \
    vim \
    htop && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

# Install Tini: https://github.com/krallin/tini
ENV TINI_VERSION v0.18.0
RUN wget --quiet --no-check-certificate https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini && \
    mv tini /usr/local/bin/tini && \
    chmod +x /usr/local/bin/tini

# Configure environment; set USER to your ID (make sure to do it on two positions)
ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    USER=vukglisovic \
    USER_ID=1000 \
    USER_GID=100 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV PATH=$CONDA_DIR/bin:$PATH \
    HOME=/home/$USER

ADD fix_permissions.sh /usr/local/bin/fix_permissions.sh
# Create user with USER_ID=1000 and in the 'users' group and make sure these dirs are writable by the `users` group.
RUN chmod 755 /usr/local/bin/fix_permissions.sh && \
    useradd -m -s /bin/bash -N -u $USER_ID $USER && \
    mkdir -p $CONDA_DIR && \
    chown $USER:$USER_GID $CONDA_DIR && \
    chmod g+w /etc/passwd /etc/group && \
    fix_permissions.sh $HOME && \
    fix_permissions.sh $CONDA_DIR

USER $USER_ID

# Setup work directory for backward-compatibility
RUN mkdir -p ${HOME}/python_scripts && \
    fix_permissions.sh ${HOME}

ENV MINICONDA_VERSION=latest
RUN cd /tmp && \
    wget https://repo.continuum.io/miniconda/Miniconda2-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    /bin/bash Miniconda2-${MINICONDA_VERSION}-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda2-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    $CONDA_DIR/bin/conda config --system --prepend channels conda-forge && \
    $CONDA_DIR/bin/conda config --system --set auto_update_conda false && \
    $CONDA_DIR/bin/conda config --system --set show_channel_urls true && \
    $CONDA_DIR/bin/conda update --all --yes && \
    $CONDA_DIR/bin/conda clean -tipsy && \
    rm -rf $HOME/.cache/yarn && \
    fix_permissions.sh $CONDA_DIR && \
    fix_permissions.sh $HOME

# Install jupyter notebook, jupyterlab and ipykernel
RUN conda install --yes \
    'jupyter' \
    'jupyterlab' \
    'ipykernel' && \
    conda clean -tipsy && \
    npm cache clean && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf $HOME/.cache/yarn && \
    fix_permissions.sh $CONDA_DIR && \
    fix_permissions.sh $HOME

RUN conda create -n dask --yes \
    'python=3.6' \
    'ipykernel' \
    'pandas' \
    'seaborn' \
    'dask' \
    'pyarrow'
#    'pulp' \
#    'statsmodels' \
#    'scikit-learn' \
#    'tensorflow' \
#    'xgboost' \
#    'lightgbm' \
#    'h5py'

# The next line creates a jupyter notebook config file and makes it possible to delete notebooks and sets a password
RUN mkdir "${HOME}/.jupyter" && \
    echo "c = get_config()" > "${HOME}/.jupyter/jupyter_notebook_config.py" && \
    echo "c.FileContentsManager.delete_to_trash = False" >> "${HOME}/.jupyter/jupyter_notebook_config.py" && \
    echo "c.NotebookApp.password = 'sha1:ec87131f6d00:1dcb46ec4fea4e951307437fd2132fd2b0ded802'" >> "${HOME}/.jupyter/jupyter_notebook_config.py" && \
    echo "c.NotebookApp.notebook_dir = '${HOME}/python_scripts'" >> "${HOME}/.jupyter/jupyter_notebook_config.py"

# change to root such that we can install new kernels for jupyter notebook
USER root

# you need to use the python executable from the environment you want to install as a kernel
RUN /opt/conda/envs/dask/bin/python -m ipykernel install --user --name dask

# jupyter is running at port 8889 (check start_jupyter.sh)
EXPOSE 8889
WORKDIR $HOME/python_scripts

# Configure container startup
ENTRYPOINT ["tini", "--"]
# When the docker is started up, start_jupyter.sh is executed.
CMD ["start_jupyter.sh"]

# Add local files as late as possible to avoid cache busting
COPY "start_jupyter.sh" "/usr/local/bin/"

# Make script for starting up jupyter executable by USER_ID user
RUN chmod 755 "/usr/local/bin/start_jupyter.sh" && \
    fix_permissions.sh $HOME

# Switch back to USER_ID user to avoid accidental container runs as root
USER $USER_ID