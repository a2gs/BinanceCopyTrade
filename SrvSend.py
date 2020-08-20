#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp
from sys import exit, argv, stderr
from os import getpid
import BinanceCTProto
import envelop_sendRecv
import socket
import zmq
import configparser

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

print(f"Starting at: [{getTimeStamp()}] PID: [{getpid()}]", file=stderr)

# --- CFG ---------------------------------

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

print('CFG:', file=stderr)

pub_name = cfgFile['GENERAL']['name']

pub_address = cfgFile['PUBLISHER']['address']
pub_topic   = cfgFile['PUBLISHER']['topic']

signalSource_port    = cfgFile['SIGNAL_SOURCE']['port']
signalSource_address = cfgFile['SIGNAL_SOURCE']['address']
signalSource_maxconn = cfgFile['SIGNAL_SOURCE']['maxconnections']

print(f"Name...................: [{pub_name}]", file=stderr)
print(f"Publisher Address......: [{pub_address}]", file=stderr)
print(f"Publisher Topic........: [{pub_topic}]", file=stderr)
print(f"Signal Source Port.....: [{signalSource_port}]", file=stderr)
print(f"Signal Source Address..: [{signalSource_address}]", file=stderr)
print(f"Signal Source Max Conns: [{signalSource_maxconn}]", file=stderr)

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

	print('Waiting connections..', file=stderr)

	ret, msgret, client = conn.serverAccept()
	if ret == False:
		print(f'Connection error: [{msgret}].', file=stderr)
		exit(1)

	msgRecv = conn.recvMsg()
	conn.sendMsg(clientMsgRet, len(clientMsgRet))

	print(f'Connection from [{client}] Msg [{msgRecv}]', file=stderr)

	recv = BinanceCTProto.CT_PROTO()

	recv.loadFromNet(msgRecv)

	if recv.cmd == BinanceCTProto.CT_CMD_COPYTRADE:
		print("Received a COPYTRAPE cmd")
	elif recv.cmd == BinanceCTProto.CT_CMD_PING:
		msgpingret = "GOT PING"
		conn.sendMsg(msgpingret, len(msgpingret))
		print("PING!")
	elif recv.cmd == BinanceCTProto.CT_CMD_CANCELORDER:
		print("Received a CANCELORDER cmd")
	elif recv.cmd == BinanceCTProto.CT_CMD_GETOPENORDERS:
		print("Received a GETOPENORDERS cmd")
	else:
		print(f"Unknow protocol: [{recv.formatToNet()}")

	ds = f"{pub_topic} {recv.formatToNet()}"

	print(f"SENDING: [{ds}]", file=stderr)

	pub_socket.send_string(ds, encoding='utf-8')
