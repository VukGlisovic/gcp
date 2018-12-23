#!/usr/bin/env bash

read -p "Enter the compute name to copy bash files to:" VM_NAME

ZONE=$(gcloud compute instances list | grep ${VM_NAME} | awk '{print $2}')
echo "Corresponding zone: ${ZONE}"

COPY_FROM="${HOME}/gcp/compute_engine/bash_scripts"

gcloud compute scp --recurse "${COPY_FROM}" "${VM_NAME}:/home/vukglisovic/" --zone ${ZONE}
