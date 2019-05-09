#!/usr/bin/env bash

# Script for setting up vm with jupyter
echo "Setting up basic stuff."
sudo apt-get update
echo y | sudo apt-get install htop pigz unzip gcc

# Add stuff to .bashrc
echo -e "\n# HISTORY\nHISTSIZE=90000\nHISTCONTROL='ignoreboth'\nshopt -s histappend\n#export PROMPT_COMMAND='history -a; history -n'" >> $HOME/.bashrc
echo "bind '\"\e[A\":history-search-backward'" >> $HOME/.bashrc
echo "bind '\"\e[B\":history-search-forward'" >> $HOME/.bashrc

# Setup python
echo "Getting latest miniconda"
MINICONDA="Miniconda3-latest-Linux-x86_64.sh"
wget https://repo.continuum.io/miniconda/${MINICONDA}
chmod 755 ${MINICONDA}
./${MINICONDA} -b -p $HOME/miniconda
echo "Installed ${MINICONDA}"
export PATH="$HOME/miniconda/bin:$PATH"
echo -e '\n# Add miniconda to path\nexport PATH="$HOME/miniconda/bin:$PATH"' >> $HOME/.bashrc
rm ${MINICONDA}
# add conda-forge channel
conda config --add channels conda-forge
echo "Installing conda, jupyter and new environment"
echo y | conda update conda
echo y | conda update --all
echo y | conda install jupyter
echo y | conda create --name py37 python=3.7 dask pandas seaborn ipykernel
source activate py37
python -m ipykernel install --user --name py37 --display-name "Python 3.7"
echo y | jupyter notebook --generate-config
# Set the password for jupyter
echo -e '{\n  "NotebookApp": {\n    "password": "sha1:2dcb797ca58d:f871caa9ab82ea50d0c69812d37519814dbe9c5f"\n  }\n}' > $HOME/.jupyter/jupyter_notebook_config.json
echo "Finished installing conda, etc."
mkdir notebooks

echo "Finished setup of vm!"
