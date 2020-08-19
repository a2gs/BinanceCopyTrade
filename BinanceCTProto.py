#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from BinanceCTUtil import getTimeStamp

CT_CMD_COPYTRADE = "COPYTRADE"
CT_CMD_CANCELORDER = "CANCEL ORDER"
CT_CMD_GETOPENORDERS = "OPENORDERS"

CT_TYPE_RESPONSE = "RESP"
CT_TYPE_REQUEST  = "REQ"

'''
{
	cmd : "cmd_type",
	fromto { from : "from name", to: "to_name" },
	timestamp : "YYYY-MM-DD hh:mm:ss.miiiii",
	type : "RESPONSE",
	response_timestamp : "YYYY-MM-DD hh:mm:ss.miiiii",
	data { symbol : "BTCUSDT", side : "BUY", type : "LIMIT", price : "0.000" }
}
'''

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
		pass

	def loadFromNet(self):
		pass

class CT_PROTO_CANCELORDER_DATA:
	server_order_id = ""

	def __init__(self):
		self.server_order_id = ""

class CT_PROTO_GETOPENORDERS:
	class CT_PROTO_GETOPENORDERS_INFO:
		symbol = ""
		ordid = ""
		side = ""
		ordtype = ""
		price = ""
		server_order_id_ref = ""

		def __init__(self):
			self.symbol = ""
			self.ordid = ""
			self.side = ""
			self.ordtype = ""
			self.price = ""
			self.server_order_id_ref = ""

	open_orders = []

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
