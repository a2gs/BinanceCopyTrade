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

cfgFile = configparser.ConfigParser()
cfgFile.read(argv[1])

ctm_name = cfgFile['GENERAL']['name']

ctm_signalSource_port = cfgFile['SIGNAL_SOURCE']['port']
ctm_signalSource_address = cfgFile['SIGNAL_SOURCE']['address']

# --- SOCKET - SAMPLE 1 -------------------

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

copytrade_sample1.data = BinanceCTProto.CT_PROTO_COPYTRADE_DATA()
copytrade_sample1.data.symbol = "BTCUSDT"
copytrade_sample1.data.side = "BUY"
copytrade_sample1.data.ordid = "1234567890"
copytrade_sample1.data.ordtype = "LIMIT"
copytrade_sample1.data.price = "10.10101010"

msg = copytrade_sample1.formatToNet()

con.sendMsg(msg, len(msg))
msgRecv = con.recvMsg()
con.endClient()

print(f'Sent: [{msg}]\nReceived: [{msgRecv}]', file=stderr)

# --- SOCKET - SAMPLE 2 -------------------

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

cancelorder_sample1.data = BinanceCTProto.CT_PROTO_CANCELORDER_DATA()
cancelorder_sample1.data.server_order_id  = 666

msg = cancelorder_sample1.formatToNet()
con.sendMsg(msg, len(msg))
msgRecv = con.recvMsg()

con.endClient()

print(f'Sent: [{msg}]\nReceived: [{msgRecv}]', file=stderr)

# --- SOCKET - SAMPLE 3 -------------------

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

ordAAA = BinanceCTProto.CT_PROTO_GETOPENORDERS.CT_PROTO_GETOPENORDERS_INFO()
'''
ordAAA['symbol'] = "A"
ordAAA['ordid'] = "AA"
ordAAA['side'] = "AAA"
ordAAA['ordtype'] = "AAAAA"
ordAAA['price'] = "AAAAAAAA"
ordAAA['server_order_id_ref'] = "AAAAAAAAAAA"
'''

ordBBB = BinanceCTProto.CT_PROTO_GETOPENORDERS.CT_PROTO_GETOPENORDERS_INFO()
'''
ordBBB['symbol'] = "B"
ordBBB['ordid'] = "BB"
ordBBB['side'] = "BBB"
ordBBB['ordtype'] = "BBBB"
ordBBB['price'] = "BBBBB"
ordBBB['server_order_id_ref'] = "BBBBBBBBB"
'''

ordCCC = BinanceCTProto.CT_PROTO_GETOPENORDERS.CT_PROTO_GETOPENORDERS_INFO()
'''
ordCCC['symbol'] = "C"
ordCCC['ordid'] = "CC"
ordCCC['side'] = "CCC"
ordCCC['ordtype'] = "CCCC"
ordCCC['price'] = "CCCCC"
ordCCC['server_order_id_ref'] = "CCCCCCC"
'''

getopenorders_sample1.data.open_orders.append(ordAAA)
getopenorders_sample1.data.open_orders.append(ordBBB)
getopenorders_sample1.data.open_orders.append(ordCCC)

msg = getopenorders_sample1.formatToNet()

con.sendMsg(msg, len(msg))
msgRecv = con.recvMsg()
con.endClient()

print(f'Sent: [{msg}]\nReceived: [{msgRecv}]', file=stderr)


# -----------------------------------------
