#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from sys import argv, exit
import socket
import envelop_sendRecv
import configparser

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

# --- CFG ---------------------------------

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

srvDataClient_name = cfgFile['GENERAL']['name']

signalSrvDataClient_port = cfgFile['SIGNAL_SOURCE']['port']
signalSrvDataClient_address = cfgFile['SIGNAL_SOURCE']['address']
signalSrvDataClient_maxconn = cfgFile['SIGNAL_SOURCE']['maxconnections']

db_engine = cfgFile['DB']['engine']
if db_engine == 'sqlite':
	db_file = cfgFile['DB']['file']
elif db_engine == 'postgresql':
	db_user = cfgFile['DB']['user']
	db_pass = cfgFile['DB']['pass']
	db_port = cfgFile['DB']['port']
	db_schema = cfgFile['DB']['schema']
else:
	print("Undefined DB engine config!")
	exit(1)

del cfgFile

# --- SOCKET ------------------------------

con = envelop_sendRecv.connection()
con.serverLoad(socket.AF_INET, socket.SOCK_STREAM)
con.sockOpts(socket.SO_REUSEADDR)
con.serverBindListen(int(signalSrvDataClient_port), int(signalSrvDataClient_maxconn))

while True:
	print("Wating connection...")

	client = con.serverAccept()

	msgRecv = con.recvMsg()

	print(f'Connection from [{client}]. Msg: [{msgRecv}]')

	respRet = "Ok"
	con.sendMsg(respRet, len(respRet))

	con.endClient()

print("End Srv Data Client")
con.endServer()
