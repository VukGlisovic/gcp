#!/usr/bin/env bash

SOURCE_DIR=""$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )""
VE_DIR="${SOURCE_DIR}/ve"
REQUIREMENTS_FILE="${SOURCE_DIR}/requirements.txt"

echo "Removing old environment."
rm -rf ${VE_DIR}

echo "Creating new environment."
virtualenv -p python3 ${VE_DIR}

source ${VE_DIR}/bin/activate

pip install -r ${REQUIREMENTS_FILE}
