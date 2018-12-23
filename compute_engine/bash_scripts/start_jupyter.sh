#!/usr/bin/env bash

echo "Starting jupyter notebook in the background with nohup. You can kill the terminal now without killing the jupyter notebook session."
LOG_DIR="${HOME}/jupyter.log"
NOTEBOOK_DIR="${HOME}/notebooks"
nohup jupyter notebook --port=9999 --ip=0.0.0.0 --notebook-dir=${NOTEBOOK_DIR} --no-browser &> ${LOG_DIR} &
echo ""
sleep 2
echo "Retrieving the host port for the command for the client to connect to the vm jupyter."

VM_NAME=$(curl -H Metadata-Flavor:Google http://metadata/computeMetadata/v1/instance/hostname | cut -d. -f1)
VM_ZONE=$(curl -H Metadata-Flavor:Google http://metadata/computeMetadata/v1/instance/zone | cut -d/ -f4)
HOST_PORT=$(ps aux | grep -w jupyter-notebook | grep port | awk '{print $13}' | grep -o -E "[0-9]+")
if [ ! -z ${HOST_PORT} ]
then
    echo "Found host port ${HOST_PORT}."
    echo "Execute the following command on the client machine to get access."
    echo "gcloud compute ssh --zone ${VM_ZONE} ${VM_NAME} -- -L 9999:localhost:${HOST_PORT}" -L 8787:localhost:8787
else
    echo "No port found. Either jupyter hasn't started up yet, but probably something went wrong while starting up."
    echo "Checkout the logs here: ${LOG_DIR}"
fi
