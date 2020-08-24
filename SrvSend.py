#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp
from sys import exit, argv, stderr
from os import getpid
from signal import signal, SIGILL, SIGTRAP, SIGINT, SIGHUP, SIGTERM, SIGSEGV, SIGUSR1, SIGPIPE, SIGIO
import BinanceCTDB
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

	logging.debug(f"Exit with code [{num}]")
	exit(num)

def execCmdCopytradeReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, BinanceCTProto.CT_PROTO, BinanceCTProto.CT_PROTO]: 

	ret, retmsg = srvDB.DB.insertCmd(recv)
	if ret == False:
		return([False, f"Database error inserting recv cmd [{retmsg}]", None, None])

	srvSendTimestamp = getTimeStamp()

	# Message to clients (pub/sub)
	sendForward = BinanceCTProto.CT_PROTO(_cmd            = BinanceCTProto.CT_CMD_COPYTRADE,
	                                      _fromto_from    = recv.fromto['from'],
	                                      _fromto_to      = recv.fromto['to'],
	                                      _timestamp      = recv.timestamp,
	                                      _cmdtype        = recv.cmdtype, # must be: BinanceCTProto.CT_TYPE_REQUEST
	                                      _resp_timestamp = srvSendTimestamp, # Client will receive the SrvSend timestamp
	                                      _data           = recv.data)

	ret, retmsg = srvDB.DB.insertCmd(sendForward)
	if ret == False:
		sendResponseErr = BinanceCTProto.CT_PROTO(_cmd            = BinanceCTProto.CT_CMD_COPYTRADE,
		                                          _fromto_from    = recv.fromto['to'],
		                                          _fromto_to      = recv.fromto['from'],
		                                          _timestamp      = srvSendTimestamp,
		                                          _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
		                                          _resp_timestamp = recv.timestamp,
		                                          _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_COPYTRADE_ERROR1, "Insert sendForward error"))
		return([False, f"Database error inserting forward cmd [{retmsg}]", None, sendResponse])

	# Message response to CopyTrade
	sendResponse = BinanceCTProto.CT_PROTO(_cmd            = BinanceCTProto.CT_CMD_COPYTRADE,
	                                       _fromto_from    = recv.fromto['to'],
	                                       _fromto_to      = recv.fromto['from'],
	                                       _timestamp      = srvSendTimestamp,
	                                       _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
	                                       _resp_timestamp = recv.timestamp,
	                                       _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_RESP_OK, "Ok"))

	ret, retmsg = srvDB.DB.insertCmd(sendResponse)
	if ret == False:
		sendResponseErr = BinanceCTProto.CT_PROTO(_cmd            = BinanceCTProto.CT_CMD_COPYTRADE,
		                                          _fromto_from    = recv.fromto['to'],
		                                          _fromto_to      = recv.fromto['from'],
		                                          _timestamp      = srvSendTimestamp,
		                                          _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
		                                          _resp_timestamp = recv.timestamp,
		                                          _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_COPYTRADE_ERROR2, "Insert sendResponse error"))
		return([False, f"Database error inserting response cmd [{retmsg}]", None, sendResponseErr])

	return([True, "Ok", sendForward, sendResponse])

def execCmdPingReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, BinanceCTProto.CT_PROTO, BinanceCTProto.CT_PROTO]:

	sendBadResponse = BinanceCTProto.CT_PROTO(_cmd            = recv.cmd,
	                                          _fromto_from    = recv.fromto['to'],
	                                          _fromto_to      = recv.fromto['from'],
	                                          _timestamp      = getTimeStamp(),
	                                          _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
	                                          _resp_timestamp = recv.timestamp,
	                                          _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_RESP_PING, "Ping resp"))

	return([True, "Ok", recv, sendResponse])

def execCmdCancelOrderReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, BinanceCTProto.CT_PROTO, BinanceCTProto.CT_PROTO]:

	# TODO: send cancel order to pubsub

	sendResponse = BinanceCTProto.CT_PROTO(_cmd            = recv.cmd,
	                                       _fromto_from    = recv.fromto['to'],
	                                       _fromto_to      = recv.fromto['from'],
	                                       _timestamp      = getTimeStamp(),
	                                       _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
	                                       _resp_timestamp = recv.timestamp,
	                                       _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_RESP_OK, "Ok"))

	return([True, "Ok", None, sendResponse])

def execCmdGetOpenOrdersReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, BinanceCTProto.CT_PROTO, BinanceCTProto.CT_PROTO]:

	# TODO: send get open orders to pubsub

	sendResponse = BinanceCTProto.CT_PROTO(_cmd            = recv.cmd,
	                                       _fromto_from    = recv.fromto['to'],
	                                       _fromto_to      = recv.fromto['from'],
	                                       _timestamp      = getTimeStamp(),
	                                       _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
	                                       _resp_timestamp = recv.timestamp,
	                                       _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_RESP_OK, "Ok"))

	return([True, "Ok", None, sendResponse])

def sendToPUBSUB(pubsock, topic : str = "", msg : str = "")->[bool, str]:

	sendToNet = f"{topic} {msg}"
	logging.debug(f"SENDING PUBSUB: [{sendToNet}]")

	try:
		pubsock.send_string(sendToNet, encoding='utf-8')

	except zmq.ZMQError as e:
		return([False, f"Error sendToPUBSUB ZMQError: [{e.errno}] [{e.msg}]"])
	except zmq.Again as e:
		return([False, f"Error sendToPUBSUB Again: [{e.errno}] [{e.msg}]"])
	except zmq.ContextTerminated as e:
		return([False, f"Error sendToPUBSUB ContextTerminated: [{e.errno}] [{e.msg}]"])
	except zmq.NotDone as e:
		return([False, f"Error sendToPUBSUB NotDone: [{e.errno}] [{e.msg}]"])
	except zmq.ZMQBindError as e:
		return([False, f"Error sendToPUBSUB ZMQBindError: [{e.errno}] [{e.msg}]"])

	return([True, "Ok"])

def sigHandler(signum, frame):

	if signum == SIGUSR1:
		logging.info('Singal SIGUSR1 received! Normal shutdown returning [0] to shell.\n')
		safeExit(0)

	else:
		logging.info(f'Singal {signum} received! Return [1] to shell.\n')
		safeExit(1)

signal(SIGILL , sigHandler)
signal(SIGTRAP, sigHandler)
signal(SIGINT , sigHandler)
signal(SIGHUP , sigHandler)
signal(SIGTERM, sigHandler)
signal(SIGSEGV, sigHandler)
signal(SIGUSR1, sigHandler)
signal(SIGPIPE, sigHandler)
signal(SIGIO, sigHandler)

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
	                    level    = logging.INFO,
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

	recv = BinanceCTProto.CT_PROTO()

	recv.loadFromNet(msgRecv)

	logging.debug(f'Msg: [{msgRecv}]')
	logging.info(f"-------------------------------")
	logging.info(f"RECEIVED FROM SOCKET [{client[0]}:{client[1]}]:")
	BinanceCTProto.dumpCmdToLog(recv, logging.info)

	# here we may place a recv.fromto['from'] validation through a "valid CopyTrade clients" list from config file. at first we will execute from ALL incoming.

	if recv.cmd == BinanceCTProto.CT_CMD_COPYTRADE:

		# a CopyTrade client sent a trade.
		if recv.cmdtype == BinanceCTProto.CT_TYPE_REQUEST:
			ret, retmsg, sendForward, sendResponse = execCmdCopytradeReq(recv)
			if ret == False:
				logging.info(f"Error execCmdCopytradeReq() [{retmsg}]!")
				srvDB.DB.rollback()
				safeExit(1) # TODO: exit proc?

			srvDB.DB.commit()

		elif recv.cmdtype == BinanceCTProto.CT_TYPE_RESPONSE:
			logging.info("A RESPONSE cmd. not yet implemented (maybe... never. only in SrvDataClient).")

		else:
			logging.info(f"It is not a REQUEST neither a RESPONSE copytrade cmd: [recv.cmdtype]. Discarting!")
			sendBadResponse = BinanceCTProto.CT_PROTO(_cmd            = recv.cmd,
			                                          _fromto_from    = recv.fromto['to'],
			                                          _fromto_to      = recv.fromto['from'],
			                                          _timestamp      = getTimeStamp(),
			                                          _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
			                                          _resp_timestamp = recv.timestamp,
			                                          _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_COPYTRADE_ERROR3, "Undef CT request or response"))

	elif recv.cmd == BinanceCTProto.CT_CMD_PING:
		logging.info("PING!")
		ret, retmsg, sendForward, sendResponse = execCmdPingReq(recv)
		if ret == False:
			logging.info(f"Error execCmdPingReq() [{retmsg}]!")
			srvDB.DB.rollback()
			safeExit(1) # TODO: exit proc?

	elif recv.cmd == BinanceCTProto.CT_CMD_CANCELORDER:

		ret, retmsg, sendForward, sendResponse = execCmdCancelOrderReq(recv)
		if ret == False:
			logging.info(f"Error execCncelOrderReq() [{retmsg}]!")
			srvDB.DB.rollback()
			safeExit(1) # TODO: exit proc?

	elif recv.cmd == BinanceCTProto.CT_CMD_GETOPENORDERS:

		ret, retmsg, sendForward, sendResponse = execCmdGetOpenOrdersReq(recv)
		if ret == False:
			logging.info(f"Error execCmdGetOpenOrdersReq() [{retmsg}]!")
			srvDB.DB.rollback()
			safeExit(1) # TODO: exit proc?

	else:
		logging.info(f"Unknow protocol: [{recv.formatToNet()}]")

	# sending to PUBSUB clients
	if sendForward != None:  # if None, there is nothing to forwarda (not everything should go to pubsub)
		ret, retmsg = sendToPUBSUB(pub_socket, pub_topic, sendForward.formatToNet()) 

		logging.info(f"SENT TO PUBSUB [{pub_topic}]:")
		BinanceCTProto.dumpCmdToLog(sendForward, logging.info)

		if ret == False:
			logging.info(f"Error sendToPUBSUB() [{retmsg}]!")
			srvDB.DB.rollback()
			safeExit(1) # TODO: exit proc?

	# sending response to CopyTrade (socket)
	resp = ""
	if sendResponse != None:  # allways must be !None, .... but exeCmd...() functions could not does your correct work (these functions returns sendResponse parameters ALWAYS, EVEN IF returns ret = False).
		resp = sendResponse.formatToNet()

		logging.info("SENT TO SOCKET:")
		BinanceCTProto.dumpCmdToLog(sendResponse, logging.info)
	else:
		sendBadResponse = BinanceCTProto.CT_PROTO(_cmd            = recv.cmd,
		                                          _fromto_from    = recv.fromto['to'],
		                                          _fromto_to      = recv.fromto['from'],
		                                          _timestamp      = getTimeStamp(),
		                                          _cmdtype        = BinanceCTProto.CT_TYPE_RESPONSE,
		                                          _resp_timestamp = recv.timestamp,
		                                          _data           = BinanceCTProto.CT_PROTO_RESPONSE(BinanceCTProto.CT_PROTO_RESP_BAD_PROTO, "Bad protocol"))
		resp = sendBadResponse.formatToNet()

		logging.info("SENT TO COPYTRADE:")
		BinanceCTProto.dumpCmdToLog(sendBadResponse, logging.info)
		del sendBadResponse

	conn.sendMsg(resp, len(resp))

	del recv, resp
	del sendForward, sendResponse
