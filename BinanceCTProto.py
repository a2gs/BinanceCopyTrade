#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp
import json

CT_CMD_COPYTRADE     = "COPYTRADE"
CT_CMD_PING          = "PING"
CT_CMD_CANCELORDER   = "CANCEL ORDER"
CT_CMD_GETOPENORDERS = "OPENORDERS"

CT_TYPE_RESPONSE = "RESP"
CT_TYPE_REQUEST  = "REQ"

# Response RefNum (data['ret'])
CT_PROTO_RESP_OK          = 0
CT_PROTO_RESP_PING        = 1
CT_PROTO_RESP_BAD_PROTO   = 2
CT_PROTO_COPYTRADE_ERROR1 = 3
CT_PROTO_COPYTRADE_ERROR2 = 4
CT_PROTO_COPYTRADE_ERROR3 = 5

class CT_PROTO:
	cmd            = ""
	fromto         = {'from' : "", 'to': ""}
	timestamp      = ""
	cmdtype        = ""
	resp_timestamp = ""
	data           = object()

	def __init__(self, 
	             _cmd            = "",
	             _fromto_from    = "",
	             _fromto_to      = "",
	             _timestamp      = "",
	             _cmdtype        = "",
	             _resp_timestamp = "",
	             _data = object()):

		self.cmd            = _cmd
		self.fromto['from'] = _fromto_from
		self.fromto['to']   = _fromto_to
		self.timestamp      = _timestamp
		self.cmdtype        = _cmdtype
		self.resp_timestamp = _resp_timestamp
		self.data           = _data

	def formatToNet(self)->[bool, str]:

		msg = {
			'cmd' : self.cmd,
			'fromto' : {
				'from' : self.fromto['from'],
				'to'   : self.fromto['to']
			},
			'timestamp' : self.timestamp,
			'type' : self.cmdtype,
			'resp_timestamp' : self.resp_timestamp,
		}

		msg['data'] = {}

		try:
			if self.cmd == CT_CMD_COPYTRADE:
				if msg['type'] == CT_TYPE_REQUEST:
					msg['data']['symbol']     = self.data.symbol
					msg['data']['side']       = self.data.side
					msg['data']['ordid']      = self.data.ordid
					msg['data']['ordtype']    = self.data.ordtype
					msg['data']['qtd']        = self.data.qtd
					msg['data']['price']      = self.data.price
					msg['data']['priceStop']  = self.data.priceStop
					msg['data']['priceLimit'] = self.data.priceLimit

				elif msg['type'] == CT_TYPE_RESPONSE:
					msg['data']['ret']    = self.data.ret
					msg['data']['retmsg'] = self.data.retmsg

			elif self.cmd == CT_CMD_CANCELORDER:
				if msg['type'] == CT_TYPE_REQUEST:
					msg['data'] = { 'server_order_id' : self.data.server_order_id }

				elif msg['type'] == CT_TYPE_RESPONSE:
					msg['data']['ret']    = self.data.ret
					msg['data']['retmsg'] = self.data.retmsg

			elif self.cmd == CT_CMD_GETOPENORDERS:
				if msg['type'] == CT_TYPE_REQUEST:
					msg['data'] = { 'openorders' : [] }
					[msg['data']['openorders'].append(i.element) for i in self.data.open_orders]

				elif msg['type'] == CT_TYPE_RESPONSE:
					msg['data']['ret']    = self.data.ret
					msg['data']['retmsg'] = self.data.retmsg

		except Exception as e:
			return([False, "Index error: {e}"])

		return([True, json.dumps(msg)])

	def loadFromNet(self, msgRecv):
		jsonDump = json.loads(msgRecv)

		self.cmd            = jsonDump['cmd']
		self.fromto['from'] = jsonDump['fromto']['from']
		self.fromto['to']   = jsonDump['fromto']['to']
		self.timestamp      = jsonDump['timestamp']
		self.cmdtype        = jsonDump['type']
		self.resp_timestamp = jsonDump['resp_timestamp']

		if self.cmd == CT_CMD_COPYTRADE:
			self.data = CT_PROTO_COPYTRADE_DATA()

			if self.cmdtype == CT_TYPE_REQUEST:
				self.data.symbol     = jsonDump['data']['symbol']
				self.data.side       = jsonDump['data']['side']
				self.data.ordid      = jsonDump['data']['ordid']
				self.data.ordtype    = jsonDump['data']['ordtype']
				self.data.qtd        = jsonDump['data']['qtd']
				self.data.price      = jsonDump['data']['price']
				self.data.priceStop  = jsonDump['data']['priceStop']
				self.data.priceLimit = jsonDump['data']['priceLimit']

			elif self.cmdtype == CT_TYPE_RESPONSE:
				self.data.ret    = jsonDump['data']['ret']
				self.data.retmsg = jsonDump['data']['retmsg']

		elif self.cmd == CT_CMD_CANCELORDER:
			self.data = CT_PROTO_CANCELORDER_DATA()

			if self.cmdtype == CT_TYPE_REQUEST:
				self.data.server_order_id = jsonDump['data']['server_order_id']

			elif self.cmdtype == CT_TYPE_RESPONSE:
				self.data.ret    = jsonDump['data']['ret']
				self.data.retmsg = jsonDump['data']['retmsg']

		elif self.cmd == CT_CMD_GETOPENORDERS:
			self.data = CT_PROTO_GETOPENORDERS()

			if self.cmdtype == CT_TYPE_REQUEST:
				# TODO: copy data set
				pass

			elif self.cmdtype == CT_TYPE_RESPONSE:
				self.data.ret    = jsonDump['data']['ret']
				self.data.retmsg = jsonDump['data']['retmsg']

		else:
			self.data = None

class CT_PROTO_CANCELORDER_DATA:
	server_order_id = ""

	def __init__(self, _server_order_id = ""):
		self.server_order_id = _server_order_id

class CT_PROTO_GETOPENORDERS_INFO:
	element = {
		'symbol'              : "",
		'ordid'               : "",
		'side'                : "",
		'ordtype'             : "",
		'price'               : "",
		'server_order_id_ref' : ""
	}

	def __init__(self, _symbol = "", _ordid = "", _side = "", _ordtype = "", _price = "", _server_order_id_ref = ""):
		self.element['symbol']              = _symbol
		self.element['ordid']               = _ordid
		self.element['side']                = _side
		self.element['ordtype']             = _ordtype
		self.element['price']               = _price
		self.element['server_order_id_ref'] = _server_order_id_ref

class CT_PROTO_GETOPENORDERS:
	open_orders = []

	def __init__(self):
		self.open_orders = []

class CT_PROTO_COPYTRADE_DATA:
	symbol     = ""
	side       = ""
	ordid      = ""
	ordtype    = ""
	qtd        = ""
	price      = ""
	priceStop  = ""
	priceLimit = ""

	def __init__(self, _symbol = "", _ordid = "", _side = "", _ordtype = "", _price = "", _qtd = "", _priceLimit = "", _priceStop = ""):
		self.symbol     = _symbol
		self.ordid      = _ordid
		self.side       = _side
		self.ordtype    = _ordtype
		self.qtd        = _qtd
		self.price      = _price
		self.priceStop  = _priceStop
		self.priceLimit = _priceLimit

	def __str__(self):
		return(f"Symbol {self.symbol}|OrderId {self.ordid}|Side {self.side}|Qtd {self.qtd}|Type {self.ordtype}|Price {self.price}|StopPrice {self.priceStop}|LimitPrice {self.priceLimit}")

class CT_PROTO_RESPONSE:
	ret = 0
	retmsg = ""

	def __init__(self, _ret : int = 0, _retmsg : str = ""):
		self.ret    = _ret
		self.retmsg = _retmsg

def dumpCmdToLog(dumpCmd : CT_PROTO, log):
	log(f"Command...........: [{dumpCmd.cmd}]")
	log(f"From..............: [{dumpCmd.fromto['from']}]")
	log(f"To................: [{dumpCmd.fromto['to']}]")
	log(f"Type..............: [{dumpCmd.cmdtype}]")
	log(f"Timestamp.........: [{dumpCmd.timestamp}]")
	log(f"Response timestamp: [{dumpCmd.resp_timestamp}]")

	log("Data:")

	if dumpCmd.cmd == CT_CMD_COPYTRADE:

		if dumpCmd.cmdtype == CT_TYPE_RESPONSE:
			log(f"\tReturn........: [{dumpCmd.data.ret}]")
			log(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == CT_TYPE_REQUEST:
			log(f"\tSymbol....: [{dumpCmd.data.symbol}]")
			log(f"\tSide......: [{dumpCmd.data.side}]")
			log(f"\tId........: [{dumpCmd.data.ordid}]")
			log(f"\tQtd.......: [{dumpCmd.data.qtd}]")
			log(f"\tType......: [{dumpCmd.data.ordtype}]")
			log(f"\tPrice.....: [{dumpCmd.data.price}]")
			log(f"\tStopPrice.: [{dumpCmd.data.priceStop}]")
			log(f"\tLimitPrice: [{dumpCmd.data.priceLimit}]")

		else:
			log("Unknow data structure for this cmd type.")

	elif dumpCmd.cmd == CT_CMD_PING:
		if dumpCmd.cmdtype == CT_TYPE_RESPONSE:
			log(f"\tReturn........: [{dumpCmd.data.ret}]")
			log(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == CT_TYPE_REQUEST:
			log("\tTODO 1...")

		else:
			log("Unknow data structure for this cmd type.")

	elif dumpCmd.cmd == CT_CMD_CANCELORDER:
		if dumpCmd.cmdtype == CT_TYPE_RESPONSE:
			log(f"\tReturn........: [{dumpCmd.data.ret}]")
			log(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == CT_TYPE_REQUEST:
			log(f"\tServer order id: [{dumpCmd.data.server_order_id}]")

		else:
			log("Unknow data structure for this cmd type.")

	elif dumpCmd.cmd == CT_CMD_GETOPENORDERS:
		if dumpCmd.cmdtype == CT_TYPE_RESPONSE:
			log(f"\tReturn........: [{dumpCmd.data.ret}]")
			log(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == CT_TYPE_REQUEST:

			def printOpenOrder(log, n, order):
				log(f"\t{n}) Symbol..........: [{order['symbol']}]")
				log(f"\tOrder id...........: [{order['ordid']}]")
				log(f"\tSide...............: [{order['side']}]")
				log(f"\tOrder type.........: [{order['ordtype']}]")
				log(f"\tPrice..............: [{order['price']}]")
				log(f"\tServer order id ref: [{order['server_order_id_ref']}]")

			[printOpenOrder(log, n, i.element) for n, i in enumerate(dumpCmd.data.open_orders, 1)]

		else:
			log("Unknow data structure for this cmd type.")

	else:
		log("Unknow data structure for this cmd.")


'''
aaa = CT_PROTO(
	             _cmd            = "aaa",
	             _fromto_from    = "bbb",
	             _fromto_to      = "ccc",
	             _timestamp      = "ddd",
	             _cmdtype        = "eee",
	             _resp_timestamp = "fff")

aaa.data = CT_PROTO_COPYTRADE_DATA( _symbol = "xxx", _ordid = "yyy", _side = "zzz", _ordtype = "qqq", _price = "www")

print(aaa.data)
'''
