#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from sys import argv
import socket
import envelop_sendRecv
import configparser

import BinanceCTProto

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

# --- CFG ---------------------------------

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

ctm_name = cfgFile['GENERAL']['name']

ctm_signalSource_port = cfgFile['SIGNAL_SOURCE']['port']
ctm_signalSource_address = cfgFile['SIGNAL_SOURCE']['address']

# --- SOCKET ------------------------------

con = envelop_sendRecv.connection()
con.connectToServer(ctm_signalSource_address, int(ctm_signalSource_port), socket.AF_INET, socket.SOCK_STREAM)

# -----------------------------------------

msg = '["foo", {"bar":["baz", "abc", 1.0, 2]}]'
con.sendMsg(msg, len(msg))

msgRecv = con.recvMsg()

print(f'Sent: [{msg}] | Received: [{msgRecv}]')

con.endClient()
