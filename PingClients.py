#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from sys import argv, stderr
import BinanceCTProto
from BinanceCTUtil import getTimeStamp
from time import sleep
import socket
import envelop_sendRecv
import configparser

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

# --- CFG ---------------------------------

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

ping_name = cfgFile['GENERAL']['name']
ping_log  = cfgFile['GENERAL']['log']

ping_signalSource_port    = cfgFile['SIGNAL_SOURCE']['port']
ping_signalSource_address = cfgFile['SIGNAL_SOURCE']['address']
ping_interval             = cfgFile['SIGNAL_SOURCE']['interval']
ping_qtd                  = cfgFile['SIGNAL_SOURCE']['qtd']

# --- SOCKET ------------------------------


ping_sample1 = BinanceCTProto.CT_PROTO()
ping_sample1.cmd = BinanceCTProto.CT_CMD_PING

ping_sample1.fromto = { 'from' : ping_name, 'to': "ALL" }
ping_sample1.cmdtype = "REQ"
ping_sample1.response_timestamp = ""

ping_qtdNum = int(ping_qtd)
continuePing = True
qtdSent = 0

while continuePing == True:
	con = envelop_sendRecv.connection()
	ret, msgret = con.connectToServer(ping_signalSource_address, int(ping_signalSource_port), socket.AF_INET, socket.SOCK_STREAM)
	if ret == False:
		print(msgret, file=stderr)
		exit(1)

	ping_sample1.timestamp = getTimeStamp()
	msg = ping_sample1.formatToNet()

	con.sendMsg(msg, len(msg))
	ret, retmsg, msgRecv = con.recvMsg()
	if ret == False:
		print(f"Error: [{retmsg}]")
		exit(1)

	sleep(int(ping_interval))

	if ping_qtdNum > 0:
		qtdSent += 1
		print(f'Sent: [{msg}]\nReceived: [{msgRecv}]\nInterval [{ping_interval}]s [{qtdSent} of {ping_qtdNum}]', file=stderr)
		if qtdSent >= ping_qtdNum:
			continuePing = False
	else:
		print(f'Sent: [{msg}]\nReceived: [{msgRecv}]\nInterval [{ping_interval}] [infinitum]', file=stderr)

	con.endClient()
