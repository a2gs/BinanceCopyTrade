#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from sys import argv, stderr
import socket
import envelop_sendRecv
import configparser

from BinanceCTUtil import getTimeStamp
import BinanceCTProto

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

# --- CFG ---------------------------------

try:
	cfgFile = configparser.ConfigParser()
	cfgFile.read(argv[1])

	ctm_name = cfgFile['GENERAL']['name']
	ctm_log  = cfgFile['GENERAL']['log']

	ctm_signalSource_port    = cfgFile['SIGNAL_SOURCE']['port']
	ctm_signalSource_address = cfgFile['SIGNAL_SOURCE']['address']

except Exception as e:
	print(f"Invalid cfg file! [{e}]")
	exit(1)

del cfgFile

# --- SOCKET - SAMPLE 1 -------------------
print("--- SOCKET - SAMPLE 1 -------------------")

con = envelop_sendRecv.connection()
ret, msgret = con.connectToServer(ctm_signalSource_address, int(ctm_signalSource_port), socket.AF_INET, socket.SOCK_STREAM)
if ret == False:
	print(msgret, file=stderr)
	exit(1)

copytrade_sample1 = BinanceCTProto.CT_PROTO()
copytrade_sample1.cmd = BinanceCTProto.CT_CMD_COPYTRADE

copytrade_sample1.fromto = { 'from' : ctm_name, 'to': "anyone" }
copytrade_sample1.timestamp = getTimeStamp()
copytrade_sample1.cmdtype = "REQ"
copytrade_sample1.response_timestamp = ""

copytrade_sample1.data = BinanceCTProto.CT_PROTO_COPYTRADE_DATA(_symbol = "BTCUSDT", _side = "BUY",
                                                                _ordid = "1234567890", _ordtype = "LIMIT",
                                                                _price = "10.10101010")

msg = copytrade_sample1.formatToNet()

con.sendMsg(msg, len(msg))
ret, retmsg, msgRecv = con.recvMsg()
if ret == False:
	print(f"Error: [{retmsg}]")
	exit(1)
con.endClient()

print(f'Sent: [{msg}]\nReceived: [{msgRecv}]', file=stderr)

# --- SOCKET - SAMPLE 2 -------------------
print("--- SOCKET - SAMPLE 2 -------------------")

con = envelop_sendRecv.connection()
ret, msgret = con.connectToServer(ctm_signalSource_address, int(ctm_signalSource_port), socket.AF_INET, socket.SOCK_STREAM)
if ret == False:
	print(msgret, file=stderr)
	exit(1)

cancelorder_sample1 = BinanceCTProto.CT_PROTO()
cancelorder_sample1.cmd = BinanceCTProto.CT_CMD_CANCELORDER

cancelorder_sample1.timestamp = getTimeStamp()
cancelorder_sample1.cmdtype = "REQ"
cancelorder_sample1.response_timestamp = ""

cancelorder_sample1.data = BinanceCTProto.CT_PROTO_CANCELORDER_DATA(_server_order_id  = 666)

msg = cancelorder_sample1.formatToNet()
con.sendMsg(msg, len(msg))
msgRecv = con.recvMsg()

con.endClient()

print(f'Sent: [{msg}]\nReceived: [{msgRecv}]', file=stderr)

# --- SOCKET - SAMPLE 3 -------------------
print("--- SOCKET - SAMPLE 3 -------------------")

con = envelop_sendRecv.connection()
ret, msgret = con.connectToServer(ctm_signalSource_address, int(ctm_signalSource_port), socket.AF_INET, socket.SOCK_STREAM)
if ret == False:
	print(msgret, file=stderr)
	exit(1)

getopenorders_sample1 = BinanceCTProto.CT_PROTO()
getopenorders_sample1.cmd = BinanceCTProto.CT_CMD_GETOPENORDERS

getopenorders_sample1.timestamp = getTimeStamp()
getopenorders_sample1.cmdtype = "REQ"
getopenorders_sample1.response_timestamp = ""
getopenorders_sample1.data = BinanceCTProto.CT_PROTO_GETOPENORDERS()

ordAAA = BinanceCTProto.CT_PROTO_GETOPENORDERS_INFO(_symbol = "A", _ordid = "AA", _side = "AAA",
                                                    _ordtype = "AAAAA", _price = "AAAAAAAA",
                                                    _server_order_id_ref = "AAAAAAAAAAA")
ordBBB = BinanceCTProto.CT_PROTO_GETOPENORDERS_INFO(_symbol = "B", _ordid = "BB", _side = "BBB",
                                                    _ordtype = "BBBBB", _price = "BBBBBBBB",
                                                    _server_order_id_ref = "AAAAAAAAAAA")
ordCCC = BinanceCTProto.CT_PROTO_GETOPENORDERS_INFO(_symbol = "C", _ordid = "CC", _side = "CCC",
                                                    _ordtype = "CCCCC", _price = "CCCCCCCC",
                                                    _server_order_id_ref = "CCCCCCCCCCC")

getopenorders_sample1.data.open_orders.append(ordAAA)
getopenorders_sample1.data.open_orders.append(ordBBB)
getopenorders_sample1.data.open_orders.append(ordCCC)

msg = getopenorders_sample1.formatToNet()

con.sendMsg(msg, len(msg))
msgRecv = con.recvMsg()
con.endClient()

print(f'Sent: [{msg}]\nReceived: [{msgRecv}]', file=stderr)


# -----------------------------------------
