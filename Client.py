#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from sys import exit, argv, stderr

import zmq
import configparser
import json

import envelop_sendRecv
import socket

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException, BinanceRequestException

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

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

sub_ctx = zmq.Context()
sub_socket = sub_ctx.socket(zmq.SUB)

sub_socket.connect(sub_address)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_topic)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_name) #SELF QUEUE

print(f"SUB: [{sub_address} - {sub_topic}]", file=stderr)

# --- BINANCE CONNECTION ------------------

try:
	client = Client(binance_api, binance_sek, {"verify": True, "timeout": 20})

except BinanceAPIException as e:
	print(f"ERRO Binance connect API exception: [{e.status_code} - {e.message}]", file=stderr)
	exit(1)

except BinanceRequestException as e:
	print(f"ERRO Binance connect request exception: [{e.status_code} - {e.message}]", file=stderr)
	exit(1)

except BinanceWithdrawException as e:
	print(f"ERRO Binance connect withdraw exception: [{e.status_code} - {e.message}]", file=stderr)
	exit(1)

except Exception as e:
	print(f"ERRO Binance connection error: {e}", file=stderr)
	exit(1)

try:
	balance = client.get_asset_balance(asset='BTC')
except BinanceAPIException as e:
	print(f"ERRO Binance get_asset_balance API exception: [{e.status_code} - {e.message}]", file=stderr)
	exit(1)
except BinanceRequestException as e:
	print(f"ERRO Binance get_asset_balance request exception: [{e.status_code} - {e.message}]", file=stderr)
	exit(1)

print(f"Free BTC account balance: [{balance['free']}]", file=stderr)

# -----------------------------------------

while True:
	try:
		msg = sub_socket.recv_string(encoding='utf-8')
	except OSError as e:
		print(f"OS Exception: {e.errno} {e.strerror}")
		exit(1)
	except KeyboardInterrupt:
		print("KeyboardInterrupt (Ctrl-C)")
		exit(1)
	except Exception as e:
		print("0Mq Exception: [{e}]")
		exit(1)
	except BaseException as e:
		print(f"BaseException {str(e)}")
		exit(1)
	except:
		print("Unknow exception")
		exit(1)

	dt = msg[:len(sub_topic)]
	ds = msg[len(sub_topic)+1:]
	print(f"TOPIC: [{dt}] MSG: [{ds}]")

	d = json.loads(ds)
	'''
	print(d[0])
	print(d[1])
	print(d[1]['bar'])
	print(d[1]['bar'][1])
	'''

	msg = "Got trade!"

	con = envelop_sendRecv.connection()
	con.connectToServer(srv_dataclient_address, int(srv_dataclient_port), socket.AF_INET, socket.SOCK_STREAM)

	con.sendMsg(msg, len(msg))

	ret, retmsg, msgRecv = con.recvMsg()
	if ret == False:
		print(f"Error: [{retmsg}]")
		exit(1)

	print(f'Sent: [{msg}] | Received: [{msgRecv}]')

	print("------------------------------")
