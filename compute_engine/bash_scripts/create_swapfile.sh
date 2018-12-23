#!/usr/bin/env bash

# Create the file to be used for swap
sudo fallocate -l 40G /mnt/40GB.swap
# Format the file for swap
sudo mkswap /mnt/40GB.swap
# Add the file to the system as a swap file
sudo swapon /mnt/40GB.swap
# Check that the swapfile was created
sudo swapon -s
