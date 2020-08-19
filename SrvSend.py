#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from sys import exit, argv
from time import sleep
import envelop_sendRecv
import socket
import zmq
import configparser
import json

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

# --- CFG ---------------------------------

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

pub_name = cfgFile['GENERAL']['name']

pub_address = cfgFile['PUBLISHER']['address']
pub_topic  = cfgFile['PUBLISHER']['topic']

signalSource_port = cfgFile['SIGNAL_SOURCE']['port']
signalSource_address = cfgFile['SIGNAL_SOURCE']['address']
signalSource_maxconn = cfgFile['SIGNAL_SOURCE']['maxconnections']

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

# --- PUB/SUB -----------------------------

pub_ctx = zmq.Context()
pub_socket = pub_ctx.socket(zmq.PUB)
pub_socket.bind(pub_address)

# --- SOCKET ------------------------------

conn = envelop_sendRecv.connection()
conn.serverLoad(socket.AF_INET, socket.SOCK_STREAM)
conn.sockOpts(socket.SO_REUSEADDR)
conn.serverBindListen(int(signalSource_port), int(signalSource_maxconn))

# -----------------------------------------

while True:
	clientMsgRet = "Ok"

	client = conn.serverAccept()

	msgRecv = conn.recvMsg()
	conn.sendMsg(clientMsgRet, len(clientMsgRet))

	print(f'Connection from [{client}] Msg [{msgRecv}]')

	d = json.loads(msgRecv)
	ds = f"{pub_topic} {json.dumps(d)}"

	print(f"SENDING: [{ds}]")

	pub_socket.send_string(ds, encoding='utf-8')
