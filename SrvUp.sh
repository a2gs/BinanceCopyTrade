#!/usr/bin/env bash

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

# Script exit if a command fails:
#set -e

# Script exit if a referenced variable is not declared:
#set -u

# If one command in a pipeline fails, its exit code will be returned as the result of the whole pipeline:
#set -o pipefail

# Activate tracing:
#set -x

source venv/bin/activate

rm -rf log/SrvDataClient.log log/SrvSend.log

./SrvDataClient.py ./cfg/SrvDataClient.cfg &
./SrvSend.py ./cfg/SrvSend.cfg &
