#!/bin/bash

set -e

ROLE=$(curl -f -s -H Metadata-Flavor:Google http://metadata/computeMetadata/v1/instance/attributes/dataproc-role)

if [[ "${ROLE}" == 'Master' ]]; then
    echo "Installation for master running"
else
    echo "Installation for a worker running"
fi

echo "Pulling conda bootstrap script from public cloud storage bucket."
gsutil -m cp -r gs://dataproc-initialization-actions/conda/bootstrap-conda.sh .
# gsutil -m cp -r gs://dataproc-initialization-actions/conda/install-conda-env.sh .

chmod 755 ./*conda*.sh

echo "Install Miniconda / conda"
./bootstrap-conda.sh

source /etc/profile
echo "which pip"
which pip

# conda install pip
conda install pip

echo "again which pip"
which pip

echo "Installing google packages"
# pip install --upgrade --no-cache-dir --ignore-installed google-cloud==0.24.0
pip install --upgrade --no-cache-dir --ignore-installed \
    google-api-python-client==1.7.7 \
    google-cloud-storage==1.13.0

echo "Installing other packages"
pip install --upgrade --no-cache-dir \
    pandas==0.23.4

echo "Installation completed"