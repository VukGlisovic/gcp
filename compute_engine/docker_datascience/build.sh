#!/usr/bin/env bash

# how to enter an intermediate image and debug what is going on:
# docker run --rm -it <id_last_working_layer> bash -il

sudo docker build --rm -t datascience .
