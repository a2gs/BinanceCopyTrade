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

	def formatToNet(self)->str:

		msg = {
			'cmd' : self.cmd,
			'fromto' : {
				'from' : self.fromto['from'],
				'to'   : self.fromto['to']
			},
			'timestamp' : self.timestamp,
			'type'      : self.cmdtype,
			'resp_timestamp' : self.resp_timestamp,
		}

		if self.cmd == CT_CMD_COPYTRADE:
			msg['data'] = {}

			msg['data']['symbol']  = self.data.symbol
			msg['data']['side']    = self.data.side
			msg['data']['ordid']   = self.data.ordid
			msg['data']['ordtype'] = self.data.ordtype
			msg['data']['price']   = self.data.price

		elif self.cmd == CT_CMD_CANCELORDER:
			msg['data'] = {
				'server_order_id' : self.data.server_order_id
			}
		elif self.cmd == CT_CMD_GETOPENORDERS:
			msg['data'] = {
				'openorders' : []
			}
		
			[msg['data']['openorders'].append(i.element) for i in self.data.open_orders]

		return json.dumps(msg)

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

			self.data.symbol  = jsonDump['data']['symbol']
			self.data.side    = jsonDump['data']['side']
			self.data.ordid   = jsonDump['data']['ordid']
			self.data.ordtype = jsonDump['data']['ordtype']
			self.data.price   = jsonDump['data']['price']

		elif self.cmd == CT_CMD_CANCELORDER:
			self.data = CT_PROTO_CANCELORDER_DATA()
			# TODO: copy data set

		elif self.cmd == CT_CMD_GETOPENORDERS:
			self.data = CT_PROTO_GETOPENORDERS()
			# TODO: copy data set

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
	symbol  = ""
	side    = ""
	ordid   = ""
	ordtype = ""
	price   = ""

	def __init__(self, _symbol = "", _ordid = "", _side = "", _ordtype = "", _price = ""):
		self.symbol  = _symbol
		self.ordid   = _ordid
		self.side    = _side
		self.ordtype = _ordtype
		self.price   = _price
