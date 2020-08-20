#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp
import json

CT_CMD_COPYTRADE = "COPYTRADE"
CT_CMD_CANCELORDER = "CANCEL ORDER"
CT_CMD_GETOPENORDERS = "OPENORDERS"

CT_TYPE_RESPONSE = "RESP"
CT_TYPE_REQUEST  = "REQ"

class CT_PROTO:
	cmd = ""
	fromto = { 'from' : "", 'to': "" }
	timestamp = ""
	cmdtype = ""
	response_timestamp = ""
	data = {}

	def __init__(self):
		self.cmd = ""
		self.fromto = { 'from' : "", 'to': "" }
		self.timestamp = ""
		self.cmdtype = ""
		self.response_timestamp = ""
		self.data = {}

	def formatToNet(self)->str:

		msg = {
			'cmd' : self.cmd,
			'fromto' : {
				'from' : self.fromto['from'],
				'to'   : self.fromto['to']
			},
			'timestamp' : self.timestamp,
			'type'      : self.cmdtype,
			'response_timestamp' : self.response_timestamp,
		}

		if self.cmd == CT_CMD_COPYTRADE:
			msg['data'] = {
				'symbol'  : self.data.symbol,
				'side'    : self.data.side,
				'ordid'   : self.data.ordid,
				'ordtype' : self.data.ordtype,
				'price'   : self.data.price
			}
		elif self.cmd == CT_CMD_CANCELORDER:
			msg['data'] = {
				'server_order_id' : self.data.server_order_id
			}
		elif self.cmd == CT_CMD_GETOPENORDERS:
			'''
			msg['data'] = {
				'openorders' : {}
			}
		
			[msg['data']['openorders'].append(i) for i in self.data.open_orders]
			'''

		return json.dumps(msg)

	def loadFromNet(self):
		pass

class CT_PROTO_CANCELORDER_DATA:
	server_order_id = ""

	def __init__(self):
		self.server_order_id = ""

class CT_PROTO_GETOPENORDERS:
	class CT_PROTO_GETOPENORDERS_INFO:
		element = {
			'symbol' : "",
			'ordid' : "",
			'side' : "",
			'ordtype' : "",
			'price' : "",
			'server_order_id_ref' : ""
		}

		def __init__(self):
			self.element['symbol'] = ""
			self.element['ordid'] = ""
			self.element['side'] = ""
			self.element['ordtype'] = ""
			self.element['price'] = ""
			self.element['server_order_id_ref'] = ""

	open_orders = {}

	def __init__(self):
		self.open_orders = []

class CT_PROTO_COPYTRADE_DATA:
	symbol = ""
	side = ""
	ordid = ""
	ordtype = ""
	price = ""

	def __init__(self):
		self.symbol = ""
		self.ordid = ""
		self.side = ""
		self.ordtype = ""
		self.price = ""
