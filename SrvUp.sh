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
	fi

	source "$1"/venv/bin/activate

	procToExec="$1/$2"
	procParams="$3"

	while true
	do
		echo "Starting [$procToExec $procParams]. Watchdog PID: [$$]"

		"$procToExec" "$procParams" &
		procPid=$!
		echo "$$: [$procToExec] PID: [$procPid]. Waiting..."

		wait "$procPid"
		procRet=$?

		echo -n "$$: [$procToExec] with PID [$procPid] returning [$procRet]: "
		if [ "$procRet" -eq 0 ]
		then
			echo 'Normal exit!'
			break
		else
			echo 'RERUN!'
		fi
	done
}

#WORKDIR=/home/a2gs/Desktop/Projects/BinanceCopyTrade
WORKDIR=.

runSrv "$WORKDIR" 'SrvSend.py' "$WORKDIR/cfg/SrvSend.cfg" &
runSrv "$WORKDIR" 'SrvDataClient.py' "$WORKDIR/cfg/SrvDataClient.cfg" &

echo "SrvSend and SrvDataClient watchdog running."
