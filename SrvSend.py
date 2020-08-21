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
import logging

# --- CFG ---------------------------------

try:
	cfgFile = configparser.ConfigParser()
	cfgFile.read(argv[1])

	pub_name = cfgFile['GENERAL']['name']
	pub_log = cfgFile['GENERAL']['log']

	pub_address = cfgFile['PUBLISHER']['address']
	pub_topic   = cfgFile['PUBLISHER']['topic']

	signalSource_port    = cfgFile['SIGNAL_SOURCE']['port']
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
		print("Undefined DB engine config!", file=stderr)
		exit(1)

except Exception as e:
	print(f"Invalid cfg file! [{e}]")
	exit(1)

del cfgFile

# --- LOG ---------------------------------

try:
	logging.basicConfig(filename = pub_log,
	                    level    = logging.DEBUG,
	                    format   = '%(asctime)s %(message)s',
	                    datefmt  = '%Y%m%d %H%M%S')
except:
	print(f"Erro open log file: [{pub_log}]", file=stderr)
	exit(1)

# --- PRINT CFG ---------------------------

logging.info(f"Starting at: [{getTimeStamp()}] PID: [{getpid()}]")

logging.info('Configuration:')
logging.info(f"Name...................: [{pub_name}]")
logging.info(f"Publisher Address......: [{pub_address}]")
logging.info(f"Publisher Topic........: [{pub_topic}]")
logging.info(f"Signal Source Port.....: [{signalSource_port}]")
logging.info(f"Signal Source Address..: [{signalSource_address}]")
logging.info(f"Signal Source Max Conns: [{signalSource_maxconn}]")

logging.info(f"DB Engine..............: [{db_engine}]")

if db_engine == 'sqlite':
	logging.info(f"DB File................: [{db_file}]")
elif db_engine == 'postgresql':
	logging.info(f"DB User................: [{db_user}]")
	logging.info(f"DB Port................: [{db_port}]")
	logging.info(f"DB Schema..............: [{db_schema}]")

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

def execCmdCopytradeReq()->[bool, str, object]: 
	return(True, "Ok", object())

def execCmdPingReq()->[bool, str, object]: 
	return(True, "Ok", object())

def execCmdCancelOrderReq()->[bool, str, object]: 
	return(True, "Ok", object())

def execCmdGetOpenOrdersReq()->[bool, str, object]: 
	return(True, "Ok", object())

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

while True:

	logging.info('Waiting connections..')

	ret, msgret, client = conn.serverAccept()
	if ret == False:
		logging.info(f'Connection error: [{msgret}].')
		exit(1)

	ret, retmsg, msgRecv = conn.recvMsg()
	if ret == False:
		print(f"Error: [{retmsg}]")
		exit(1)

	logging.info(f'Connection from [{client}] Msg [{msgRecv}]')

	recv = BinanceCTProto.CT_PROTO()
	sendForward = BinanceCTProto.CT_PROTO()

	recv.loadFromNet(msgRecv)

	clientMsgRet = "Ok"

	if recv.cmd == BinanceCTProto.CT_CMD_COPYTRADE:
		logging.info("Received a COPYTRAPE cmd")
		ret, retmsg, sendForward = execCmdCopytradeReq()

	elif recv.cmd == BinanceCTProto.CT_CMD_PING:
		clientMsgRet = "GOT PING"
		logging.info("PING!")
		ret, retmsg, sendForward = execCmdPingReq()

	elif recv.cmd == BinanceCTProto.CT_CMD_CANCELORDER:
		logging.info("Received a CANCELORDER cmd")
		ret, retmsg, sendForward = execCmdCancelOrderReq()

	elif recv.cmd == BinanceCTProto.CT_CMD_GETOPENORDERS:
		logging.info("Received a GETOPENORDERS cmd")
		ret, retmsg, sendForward = execCmdGetOpenOrdersReq()

	else:
		logging.info(f"Unknow protocol: [{recv.formatToNet()}]")

	ds = f"{pub_topic} {recv.formatToNet()}"

	logging.info(f"SENDING: [{ds}]")

	pub_socket.send_string(ds, encoding='utf-8')

	conn.sendMsg(clientMsgRet, len(clientMsgRet))

	del recv
	del sendForward
