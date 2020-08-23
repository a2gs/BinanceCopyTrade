#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp
from sys import exit, argv, stderr
from os import getpid
from signal import signal, SIGILL, SIGTRAP, SIGINT, SIGHUP, SIGTERM, SIGSEGV, SIGUSR1
#from BinanceCTDB import CT_DB, CT_DB_TYPE_SQLITE, CT_DB_TYPE_POSTGRESQL
import  BinanceCTDB
import BinanceCTProto
import envelop_sendRecv
import socket
import zmq
import configparser
import logging

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

def safeExit(num : int = 0):
	srvDB.DB.commit()
	srvDB.DB.quit()

	exit(num)

def execCmdCopytradeReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, BinanceCTProto.CT_PROTO]: 

	srvDB.DB.insertCmd(recv)

	sendForward = BinanceCTProto.CT_PROTO(
	             _cmd            = BinanceCTProto.CT_CMD_COPYTRADE,
	             _fromto_from    = recv.fromto['from'],
	             _fromto_to      = recv.fromto['to'],
	             _timestamp      = getTimeStamp(),
	             _cmdtype        = recv.cmdtype,
	             _resp_timestamp = recv.timestamp, # client will receive CopyTrade timestamp here
	             _data           = recv.data)

	srvDB.DB.insertCmd(sendForward)

	srvDB.DB.commit()

	return([True, "Ok", sendForward])

def execCmdPingReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, object]: 
	return([True, "Ok", recv])

def execCmdCancelOrderReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, object]: 
	return([True, "Ok", recv])

def execCmdGetOpenOrdersReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, object]: 
	return([True, "Ok", recv])

def sigHandler(signum, frame):
	if signum == SIGUSR1:
		logging.info('Singal SIGUSR1 received! Normal shutdown returning [0] to shell.\n')
		logging.shutdown()
		exit(0)
	else:
		logging.info(f'Singal {signum} received! Return [1] to shell.\n')
		logging.shutdown()
		exit(1)

signal(SIGILL , sigHandler)
signal(SIGTRAP, sigHandler)
signal(SIGINT , sigHandler)
signal(SIGHUP , sigHandler)
signal(SIGTERM, sigHandler)
signal(SIGSEGV, sigHandler)
signal(SIGUSR1, sigHandler)
#SIGPIPE
#SIGIO

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

	if db_engine == BinanceCTDB.CT_DB_TYPE_SQLITE:
		db_file = cfgFile['DB']['file']

	elif db_engine == BinanceCTDB.CT_DB_TYPE_POSTGRESQL:
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

if db_engine == BinanceCTDB.CT_DB_TYPE_SQLITE:
	logging.info(f"DB File................: [{db_file}]")
elif db_engine == BinanceCTDB.CT_DB_TYPE_POSTGRESQL:
	logging.info(f"DB User................: [{db_user}]")
	logging.info(f"DB Port................: [{db_port}]")
	logging.info(f"DB Schema..............: [{db_schema}]")

# --- DATABASE ----------------------------

srvDB = BinanceCTDB.CT_DB(_engine = db_engine, _sqliteDBFile = db_file)

ret, retmsg = srvDB.DB.connect()
if ret == False:
	logging.info(f"Error opening database: [{retmsg}]")
	exit(1)

ret, retmsg = srvDB.DB.createTablesIfNotExist()
if ret == False:
	logging.info(f"Error creating tables: [{retmsg}]")
	safeExit(1)

# --- PUB/SUB -----------------------------

pub_ctx = zmq.Context()
pub_socket = pub_ctx.socket(zmq.PUB)
pub_socket.bind(pub_address)

# --- SOCKET ------------------------------

conn = envelop_sendRecv.connection()

ret, retmsg = conn.serverLoad(socket.AF_INET, socket.SOCK_STREAM)
if ret == False:
	logging.info(f"Erro loading server: [{retmsg}]!")
	safeExit(1)

ret, retmsg = conn.sockOpts(socket.SO_REUSEADDR)
if ret == False:
	logging.info(f"Erro sockOpts server: [{retmsg}]!")
	safeExit(1)

ret, retmsg = conn.serverBindListen(int(signalSource_port), int(signalSource_maxconn))
if ret == False:
	logging.info(f"Erro binding server: [{retmsg}]!")
	safeExit(1)

# -----------------------------------------

while True:

	logging.info('Waiting connections..')

	ret, msgret, client = conn.serverAccept()
	if ret == False:
		logging.info(f'Connection error: [{msgret}].')
		safeExit(1)

	ret, retmsg, msgRecv = conn.recvMsg()
	if ret == False:
		print(f"Error: [{retmsg}]")
		safeExit(1)

	logging.info(f'Connection from [{client}] Msg [{msgRecv}]')

	recv = BinanceCTProto.CT_PROTO()
	#sendForward = BinanceCTProto.CT_PROTO()

	recv.loadFromNet(msgRecv)

	# here we may place a recv.fromto['from'] validation through a "valid CopyTrade clients" list from config file. at first we will execute from ALL incoming.

	clientMsgRet = "Ok"

	if recv.cmd == BinanceCTProto.CT_CMD_COPYTRADE:
		logging.info("Received a COPYTRAPE cmd")
		# a CopyTrade client sent a trade.
		if recv.cmdtype == BinanceCTProto.CT_TYPE_REQUEST:
			ret, retmsg, sendForward = execCmdCopytradeReq(recv)
		elif recv.cmdtype == BinanceCTProto.CT_TYPE_RESPONSE:
			logging.info("A RESPONSE cmd. not yet implemented (maybe... never. only in SrvDataClient).")
		else:
			logging.info(f"It is not a REQUEST neither a RESPONSE copytrade cmd: [recv.cmdtype]. Discarting!")
			clientMsgRet = "NOK. undef request or response"

	elif recv.cmd == BinanceCTProto.CT_CMD_PING:
		clientMsgRet = "GOT PING"
		logging.info("PING!")
		ret, retmsg, sendForward = execCmdPingReq(recv)

	elif recv.cmd == BinanceCTProto.CT_CMD_CANCELORDER:
		logging.info("Received a CANCELORDER cmd")
		ret, retmsg, sendForward = execCmdCancelOrderReq(recv)

	elif recv.cmd == BinanceCTProto.CT_CMD_GETOPENORDERS:
		logging.info("Received a GETOPENORDERS cmd")
		ret, retmsg, sendForward = execCmdGetOpenOrdersReq(recv)

	else:
		logging.info(f"Unknow protocol: [{recv.formatToNet()}]")

	ds = f"{pub_topic} {sendForward.formatToNet()}"

	logging.info(f"SENDING: [{ds}]")

	pub_socket.send_string(ds, encoding='utf-8')

	conn.sendMsg(clientMsgRet, len(clientMsgRet))

	del recv
	del sendForward
