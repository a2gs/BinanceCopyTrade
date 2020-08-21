#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp
from sys import argv, exit, stderr
from os import getpid
import socket
import envelop_sendRecv
import configparser
import logging

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

# --- CFG ---------------------------------

try:
	cfgFile = configparser.ConfigParser()
	cfgFile.read(argv[1])

	srvDataClient_name = cfgFile['GENERAL']['name']
	srvDataClient_log  = cfgFile['GENERAL']['log']

	signalSrvDataClient_port    = cfgFile['SIGNAL_SOURCE']['port']
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
		print("Undefined DB engine config!", file=stderr)
		exit(1)

except Exception as e:
	print(f"Invalid cfg file! [{e}]")
	exit(1)

del cfgFile

# --- LOG ---------------------------------

try:
	logging.basicConfig(filename = srvDataClient_log,
	                    level    = logging.DEBUG,
	                    format   = '%(asctime)s %(message)s',
	                    datefmt  = '%Y%m%d %H%M%S')
except:
	print(f"Erro open log file: [{pub_log}]", file=stderr)
	exit(1)

# --- PRINT CFG ---------------------------

logging.info(f"Starting at: [{getTimeStamp()}] PID: [{getpid()}]")

logging.info('Configuration:')
logging.info(f"Name...................: [{srvDataClient_name}]")
logging.info(f"Address................: [{signalSrvDataClient_address}]")
logging.info(f"Port...................: [{signalSrvDataClient_port}]")
logging.info(f"Signal Source Port.....: [{signalSrvDataClient_port }]")
logging.info(f"Signal Source Address..: [{signalSrvDataClient_address }]")
logging.info(f"Signal Source Max Conns: [{signalSrvDataClient_maxconn }]")

logging.info(f"DB Engine..............: [{db_engine}]")

if db_engine == 'sqlite':
	logging.info(f"DB File................: [{db_file}]")

elif db_engine == 'postgresql':
	logging.info(f"DB User................: [{db_user}]")
	logging.info(f"DB Port................: [{db_port}]")
	logging.info(f"DB Schema..............: [{db_schema}]")

# --- SOCKET ------------------------------

con = envelop_sendRecv.connection()
con.serverLoad(socket.AF_INET, socket.SOCK_STREAM)
con.sockOpts(socket.SO_REUSEADDR)
con.serverBindListen(int(signalSrvDataClient_port), int(signalSrvDataClient_maxconn))

while True:
	logging.info("Wating connection...")

	ret, msgret, client = con.serverAccept()
	if ret == False:
		logging.info(f'Connection error: [{msgret}].')
		exit(1)

	ret, retmsg, msgRecv = con.recvMsg()
	if ret == False:
		logging.info(f"Error: [{retmsg}]")
		exit(1)

	logging.info(f'Connection from [{client}]. Msg: [{msgRecv}]')

	respRet = "Ok"
	con.sendMsg(respRet, len(respRet))

	con.endClient()

logging.info("End Srv Data Client")
con.endServer()
