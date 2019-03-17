#!/usr/bin/env bash

# how to enter an intermediate image and debug what is going on:
# docker run --rm -it <id_last_working_layer> bash -il

# start new (detached) container with port forwarding (--rm removes the container after shutdown of the container):
# docker run --rm --name datascience_container -d -v /home/<path_to_your_folder>:/home/vukglisovic/python_scripts -p 8889:8889 <image_id>

# enter a running container as root user:
# sudo docker exec -it -u root <container_id> bash

sudo docker build --rm -t datascience .
