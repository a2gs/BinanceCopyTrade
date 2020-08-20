#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp
from sys import argv, exit, stderr
from os import getpid
import socket
import envelop_sendRecv
import configparser

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

print(f"Starting at: [{getTimeStamp()}] PID: [{getpid()}]", file=stderr)

# --- CFG ---------------------------------

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

print('CFG:', file=stderr)

srvDataClient_name = cfgFile['GENERAL']['name']
srvDataClient_log = cfgFile['GENERAL']['log']

signalSrvDataClient_port = cfgFile['SIGNAL_SOURCE']['port']
signalSrvDataClient_address = cfgFile['SIGNAL_SOURCE']['address']
signalSrvDataClient_maxconn = cfgFile['SIGNAL_SOURCE']['maxconnections']

print(f"Name...................: [{srvDataClient_name}]", file=stderr)
print(f"Address................: [{signalSrvDataClient_address}]", file=stderr)
print(f"Port...................: [{signalSrvDataClient_port}]", file=stderr)
print(f"Signal Source Port.....: [{signalSrvDataClient_port }]", file=stderr)
print(f"Signal Source Address..: [{signalSrvDataClient_address }]", file=stderr)
print(f"Signal Source Max Conns: [{signalSrvDataClient_maxconn }]", file=stderr)

db_engine = cfgFile['DB']['engine']
print(f"DB Engine..............: [{db_engine}]", file=stderr)

if db_engine == 'sqlite':
	db_file = cfgFile['DB']['file']
	print(f"DB File................: [{db_file}]", file=stderr)

elif db_engine == 'postgresql':
	db_user = cfgFile['DB']['user']
	db_pass = cfgFile['DB']['pass']
	db_port = cfgFile['DB']['port']
	db_schema = cfgFile['DB']['schema']
	print(f"DB User................: [{db_user}]", file=stderr)
	print(f"DB Port................: [{db_port}]", file=stderr)
	print(f"DB Schema..............: [{db_schema}]", file=stderr)

else:
	print("Undefined DB engine config!", file=stderr)
	exit(1)

del cfgFile

# --- SOCKET ------------------------------

con = envelop_sendRecv.connection()
con.serverLoad(socket.AF_INET, socket.SOCK_STREAM)
con.sockOpts(socket.SO_REUSEADDR)
con.serverBindListen(int(signalSrvDataClient_port), int(signalSrvDataClient_maxconn))

while True:
	print("Wating connection...", file=stderr)

	ret, msgret, client = con.serverAccept()
	if ret == False:
		print(f'Connection error: [{msgret}].', file=stderr)
		exit(1)

	msgRecv = con.recvMsg()

	print(f'Connection from [{client}]. Msg: [{msgRecv}]', file=stderr)

	respRet = "Ok"
	con.sendMsg(respRet, len(respRet))

	con.endClient()

print("End Srv Data Client", file=stderr)
con.endServer()
