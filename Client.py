#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from sys import exit, argv, stderr
from os import getpid

import zmq
import configparser
import json
import logging

import envelop_sendRecv
import socket
import BinanceCTProto

from BinanceCTUtil import getTimeStamp
from BinanceCTDB import CT_DB_TYPE_SQLITE, CT_DB_TYPE_POSTGRESQL

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException, BinanceRequestException

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

con = None   # Socket: signal data client
cliDB = None # Database handle

def safeExit(num : int = 0, msg : str = ""):

	if srvDB != None:
		srvDB.DB.commit()
		srvDB.DB.quit()

	if msg == "":
		logging.info(msg)

	logging.info(f"Exit with code [{num}]")
	exit(num)

def execCmdCopytradeReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, BinanceCTProto.CT_PROTO]: 

	sendForward = BinanceCTProto.CT_PROTO(
	             _cmd            = BinanceCTProto.CT_CMD_COPYTRADE,
	             _fromto_from    = recv.fromto['from'],
	             _fromto_to      = recv.fromto['to'],
	             _timestamp      = recv.timestamp, # CopyTrade timestamp
	             _cmdtype        = recv.cmdtype,
	             _resp_timestamp = recv.resp_timestamp, # should be empty (a request..)
	             _data           = recv.data)

	BinanceCTProto.dumpCmdToLog(sendForward, logging.info)

	return([True, "Ok", sendForward])

def execCmdPingReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, object]: 
	return([True, "Ok", recv])

def execCmdCancelOrderReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, object]: 
	return([True, "Ok", recv])

def execCmdGetOpenOrdersReq(recv : BinanceCTProto.CT_PROTO = None)->[bool, str, object]: 
	return([True, "Ok", recv])

# --- CFG ---------------------------------

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

sub_name = cfgFile['GENERAL']['name']
sub_log  = cfgFile['GENERAL']['log']

sub_address = cfgFile['SUB_SERVER_SEND']['address']
sub_topic   = cfgFile['SUB_SERVER_SEND']['topic']

srv_dataclient_address = cfgFile['SERVER_DATACLIENT']['address']
srv_dataclient_port    = cfgFile['SERVER_DATACLIENT']['port']

binance_api     = cfgFile['BINANCE_API']['APIKEY']
binance_sek     = cfgFile['BINANCE_API']['SEKKEY']
binance_recvwin = cfgFile['BINANCE_API']['RECVWINDOW']

db_engine = cfgFile['DB']['engine']

if db_engine == CT_DB_TYPE_SQLITE:
	db_file = cfgFile['DB']['file']

elif db_engine == CT_DB_TYPE_POSTGRESQL:
	db_user = cfgFile['DB']['user']
	db_pass = cfgFile['DB']['pass']
	db_port = cfgFile['DB']['port']
	db_schema = cfgFile['DB']['schema']

else:
	print("Undefined DB engine config!", file=stderr)
	exit(1)

del cfgFile

# --- LOG ---------------------------------

try:
	logging.basicConfig(filename = sub_log,
	                    level    = logging.INFO,
	                    format   = '%(asctime)s %(message)s',
	                    datefmt  = '%Y%m%d %H%M%S')
except:
	print(f"Erro open log file: [{sub_log}]", file=stderr)
	exit(1)

# --- PRINT CFG ---------------------------

logging.info(f"Starting at: [{getTimeStamp()}] PID: [{getpid()}]")

logging.info('Configuration:')
logging.info(f"Name.....................: [{sub_name}]")
logging.info(f"Subscriptor address......: [{sub_address}]")
logging.info(f"Subscriptor topic........: [{sub_topic}]")

logging.info(f"Signal DataClient port...: [{srv_dataclient_address }]")
logging.info(f"Signal DataClient address: [{srv_dataclient_port}]")

logging.info(f"Binance API..............: [{binance_api}]")

logging.info(f"DB Engine................: [{db_engine}]")

if db_engine == CT_DB_TYPE_SQLITE:
	logging.info(f"DB File..................: [{db_file}]")

elif db_engine == CT_DB_TYPE_POSTGRESQL:
	logging.info(f"DB User..................: [{db_user}]")
	logging.info(f"DB Port..................: [{db_port}]")
	logging.info(f"DB Schema................: [{db_schema}]")

# --- PUB/SUB -----------------------------

sub_ctx = zmq.Context()
sub_socket = sub_ctx.socket(zmq.SUB)

sub_socket.connect(sub_address)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_topic)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_name) #SELF QUEUE

# --- BINANCE CONNECTION ------------------

try:
	client = Client(binance_api, binance_sek, {"verify": True, "timeout": 20})

except BinanceAPIException as e:
	logging.info(f"ERRO Binance connect API exception: [{e.status_code} - {e.message}]")
	exit(1)

except BinanceRequestException as e:
	logging.info(f"ERRO Binance connect request exception: [{e.status_code} - {e.message}]")
	exit(1)

except BinanceWithdrawException as e:
	logging.info(f"ERRO Binance connect withdraw exception: [{e.status_code} - {e.message}]")
	exit(1)

except Exception as e:
	logging.info(f"ERRO Binance connection error: {e}")
	exit(1)

try:
	balance = client.get_asset_balance(asset='BTC')
except BinanceAPIException as e:
	logging.info(f"ERRO Binance get_asset_balance API exception: [{e.status_code} - {e.message}]")
	exit(1)
except BinanceRequestException as e:
	logging.info(f"ERRO Binance get_asset_balance request exception: [{e.status_code} - {e.message}]")
	exit(1)

logging.info(f"Free BTC account balance: [{balance['free']}]")

# -----------------------------------------

while True:
	try:
		msg = sub_socket.recv_string(encoding='utf-8')
	except OSError as e:
		logging.info(f"OS Exception: {e.errno} {e.strerror}")
		exit(1)
	except KeyboardInterrupt:
		logging.info("KeyboardInterrupt (Ctrl-C)")
		exit(1)
	except Exception as e:
		logging.info("0Mq Exception: [{e}]")
		exit(1)
	except BaseException as e:
		logging.info(f"BaseException {str(e)}")
		exit(1)
	except:
		logging.info("Unknow exception")
		exit(1)

	dt = msg[:len(sub_topic)]
	ds = msg[len(sub_topic)+1:]
	logging.info("----------------------------------\nReceived:")
	logging.debug(f"TOPIC: [{dt}]\nMSG: [{ds}]")

	recv = BinanceCTProto.CT_PROTO()
	recv.loadFromNet(ds)

	if recv.cmd == BinanceCTProto.CT_CMD_COPYTRADE:
		logging.info("Received a COPYTRAPE cmd")
		ret, retmsg, sendForward = execCmdCopytradeReq(recv)

	elif recv.cmd == BinanceCTProto.CT_CMD_PING:
		logging.info("Received a PING cmd")
		ret, retmsg, sendForward = execCmdPingReq(recv)

	elif recv.cmd == BinanceCTProto.CT_CMD_CANCELORDER:
		logging.info("Received a CANCELORDER cmd")
		ret, retmsg, sendForward = execCmdCancelOrderReq(recv)

	elif recv.cmd == BinanceCTProto.CT_CMD_GETOPENORDERS:
		logging.info("Received a GETOPENORDERS cmd")
		ret, retmsg, sendForward = execCmdGetOpenOrdersReq(recv)

	else:
		logging.info(f"Unknow protocol: [{recv.formatToNet()}]")
		#TODO: DUMP THIS MSG

	msg = "Got trade!"

	con = envelop_sendRecv.connection()

	ret, retmsg = con.connectToServer(srv_dataclient_address, int(srv_dataclient_port), socket.AF_INET, socket.SOCK_STREAM)
	if ret == False:
		logging.info(f"Connect to server error: {retmsg}")
		exit(1)

	ret, retmsg = con.sendMsg(msg, len(msg))
	if ret == False:
		logging.info(f"Send to server error: {retmsg}")
		exit(1)

	ret, retmsg, msgRecv = con.recvMsg()
	if ret == False:
		logging.info(f"Error msgRecv: [{retmsg}]")
		exit(1)

	logging.info(f'Sent: [{msg}] | Received: [{msgRecv}]')
