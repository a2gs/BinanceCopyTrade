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

function runSrv
{
	if [ "$#" -ne 3 ]
	then
		echo -e "${FUNCNAME[0]} Usage:\n\t${FUNCNAME[0]} [WORK_PATH] [EXEC] [CFG_FILE]"
		return 1
	else
		echo "OK!"
	fi

	source "$1"/venv/bin/activate

	procToExec="$1/$2"
	procCfg="$1/$3"

	while true
	do
		echo "Starting [$1 $2]"
		"$procToExec" "$procCfg" &
		procPid=$!
		echo "[$procToExec] PID: [$procPid]. Waiting..."
		wait "$procPid"
		procRet=$?
		if [ "$procRet" -ne 0 ]
		then
			echo "[$procToexec] with PID [$procPid] STOPPED returning [$procRet]!"
			break
		fi
	done
}

#WORKDIR=/home/a2gs/Desktop/Projects/BinanceCopyTrade
WORKDIR=.

runSrv "$WORKDIR" SrvSend.py cfg/SrvSend.cfg &
runSrv "$WORKDIR" SrvDataClient.py cfg/SrvDataClient.cfg &

echo 'SrvSend and SrvDataClient watchdog running.'
