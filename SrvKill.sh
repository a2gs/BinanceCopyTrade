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

pidSrvSend=`ps -ef | grep -v grep | grep SrvSend.py | awk '{print $2}'`
pidSrvDataClient=`ps -ef | grep -v grep | grep SrvDataClient.py | awk '{print $2}'`

[ ! -z "$pidSrvSend" ] && echo "SrvSend PID: [$pidSrvSend]" && kill -USR1 "$pidSrvSend"
[ ! -z "$pidSrvDataClient" ] && echo "SrvDataClient PID: [$pidSrvDataClient]" && kill -USR1 "$pidSrvDataClient"
