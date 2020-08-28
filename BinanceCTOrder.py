#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota
# andre.scota@gmail.com
# MIT license

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException, BinanceRequestException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

"""
testOrder = False
"""
LOCK = True
#LOCK = False

"""
def setTestOrder(o: bool):
	global testOrder
	testOrder = o

def getTestOrder() -> bool:
	global testOrder
	return testOrder
"""

def binanceSide(s: str):
	if   s == 'BUY':  return Client.SIDE_BUY
	elif s == 'SELL': return Client.SIDE_SELL

	return ''

# ---------------------------------------------------
def printPlacedOrder(order, log = None):
	log(f"Symbol: [{order['symbol']}]")
	log(f"\tSide.................: [{order['side']}]")
	log(f"\tType.................: [{order['type']}]")
	log(f"\tTransaction Time.....: [{order['transactTime']}]")
	log(f"\tPrice................: [{order['price']}]")
	log(f"\tOrig Qtd.............: [{order['origQty']}]")
	log(f"\tExecuted Qtd.........: [{order['executedQty']}]")
	log(f"\tCummulative Quote Qtd: [{order['cummulativeQuoteQty']}]")
	log(f"\tStatus...............: [{order['status']}]")
	log(f"\tTime In Force........: [{order['timeInForce']}]")
	log(f"\tOrder Id.............: [{order['orderId']}]")
	log(f"\tClient Order Id......: [{order['clientOrderId']}]")

	if 'fills' not in order:
		return

	for f in order['fills']:
		log(f"\t\tPrice...........: [{f['price']}]")
		log(f"\t\tQty.............: [{f['qty']}]")
		log(f"\t\tCommission......: [{f['commission']}]")
		log(f"\t\tCommission Asset: [{f['commissionAsset']}]")

def cancel_a_spot_order(client, log = None, symbOrd = '', ordrid = 0) -> [bool, str]:
	log(f"Cancel SPOT Order Id [{ordrid}] with Symbol [{symbOrd}]")

	# TESTING
	global LOCK
	if LOCK == True:
		return False, "Programmed flag order lock ON!"

	try:
		cancOrd = client.cancel_order(symbol = symbOrd, orderId = ordrid)
	except BinanceRequestException as e:
		return False, f"Erro BinanceRequestException: [{e.status_code} - {e.message}]"
	except BinanceAPIException as e:
		return False, f"Erro at client.cancel_order() BinanceAPIException: [{e.status_code} - {e.message}]"
	except Exception as e:
		return False, f"Erro at client.cancel_order(): {e}"

	log(f"Symbol..................: [{cancOrd['symbol']}]")
	log(f"Original Client Order Id: [{cancOrd['origClientOrderId']}]")
	log(f"Order Id................: [{cancOrd['orderId']}]")
	log(f"Order List Id (OCO info): [{cancOrd['orderListId']}]")
	log(f"Client Order Id.........: [{cancOrd['clientOrderId']}]")
	log(f"Price...................: [{cancOrd['price']}]")
	log(f"Original Qtd............: [{cancOrd['origQty']}]")
	log(f"Executed Qty............: [{cancOrd['executedQty']}]")
	log(f"Cummulative Quote Qty...: [{cancOrd['cummulativeQuoteQty']}]")
	log(f"Status..................: [{cancOrd['status']}]")
	log(f"Time In Force...........: [{cancOrd['timeInForce']}]")
	log(f"Type....................: [{cancOrd['type']}]")
	log(f"Side....................: [{cancOrd['side']}]")

	return True, "Ok"

def cancel_a_margin_order(client, log, symbOrd = '', ordrid = 0) -> [bool, str]:
	log(f"Cancel Margin Order Id [{ordrid}] with Symbol [{symbOrd}]")

	# TESTING
	global LOCK
	if LOCK == True:
		return False, "Programmed flag order lock ON!"

	try:
		cancOrd = client.cancel_margin_order(symbol = symbOrd, orderId = ordrid)
	except BinanceRequestException as e:
		return False, f"Erro at client.cancel_margin_order() BinanceRequestException: [{e.status_code} - {e.message}]"

	except BinanceAPIException as e:
		return False, f"Erro at client.cancel_margin_order() BinanceAPIException: [{e.status_code} - {e.message}]"

	except Exception as e:
		return False, f"Erro at client.cancel_margin_order(): {e}"

	log(f"Symbol..................: [{cancOrd['symbol']}]")
	log(f"Original Client Order Id: [{cancOrd['origClientOrderId']}]")
	log(f"OrderId.................: [{cancOrd['orderId']}]")
	log(f"Client Order Id.........: [{cancOrd['clientOrderId']}]")
	log(f"Price...................: [{cancOrd['price']}]")
	log(f"Original Qtd............: [{cancOrd['origQty']}]")
	log(f"Executed Qty............: [{cancOrd['executedQty']}]")
	log(f"Cummulative Quote Qty...: [{cancOrd['cummulativeQuoteQty']}]")
	log(f"Status..................: [{cancOrd['status']}]")
	log(f"Time In Force...........: [{cancOrd['timeInForce']}]")
	log(f"Type....................: [{cancOrd['type']}]")
	log(f"Side....................: [{cancOrd['side']}]")

	return True, 'Ok'

# ---------------------------------------------------

def orderSpotLimit(client, log = None, symbOrd = '', qtdOrd = 0, prcOrd = 0.0,
                   prcStopOrd = 0.0, prcStopLimitOrd = 0.0, sideOrd = 0) -> [bool, str, str]:

	log(f"Symbol....: [{symbOrd}]")
	log(f"Side......: [{sideOrd}]")
	log(f"Quantity..: [{qtdOrd}]")
	log(f"Price.....: [{prcOrd}]")
	log(f"Stop Price: [{prcStopOrd}]")
	log(f"Limit OCO.: [{prcStopLimitOrd}]")

	# TESTING
	global LOCK
	if LOCK == True:
		return([False, "Programmed flag order lock ON!", ""])

	try:
		order = client.create_oco_order(symbol               = symbOrd,
		                                side                 = sideOrd,
		                                quantity             = qtdOrd,
		                                price                = prcOrd,
		                                stopPrice            = prcStopOrd,
												  stopLimitPrice       = prcStopLimitOrd,
		                                stopLimitTimeInForce = Client.TIME_IN_FORCE_GTC,
		                                newOrderRespType     = Client.ORDER_RESP_TYPE_FULL)

	except BinanceRequestException as e:
		return([False, f"Erro create_oco_order BinanceRequestException: [{e.status_code} - {e.message}]", ""])
	except BinanceAPIException as e:
		return([False, f"Erro create_oco_order BinanceAPIException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderException as e:
		return([False, f"Erro create_oco_order BinanceOrderException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinAmountException as e:
		return([False, f"Erro create_oco_order BinanceOrderMinAmountException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinPriceException as e:
		return([False, f"Erro create_oco_order BinanceOrderMinPriceException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinTotalException as e:
		return([False, f"Erro create_oco_order BinanceOrderMinTotalException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderUnknownSymbolException as e:
		return([False, f"Erro create_oco_order BinanceOrderUnknownSymbolException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderInactiveSymbolException as e:
		return([False, f"Erro create_oco_order BinanceOrderInactiveSymbolException: [{e.status_code} - {e.message}]", ""])
	except Expcetion as e:
		return([False, f"Erro create_oco_order generic exception: {e}", ""])

	printPlacedOrder(order, log, order['orderId'])

	return True, "Ok"

def orderSpot(client, log = None, symbOrd = '', qtdOrd = 0, prcOrd = 0.0, sideOrd = 0, typeOrd = 0) ->[bool, str, str]:

	log(f"Symbol....: [{symbOrd}]")
	log(f"Side......: [{sideOrd}]")
	log(f"Quantity..: [{qtdOrd}]")
	log(f"Price.....: [{prcOrd}]")
	log(f"Type......: [{typeOrd}]")

	# TESTING
	global LOCK
	if LOCK == True:
#		return([False, "Programmed flag order lock ON!", ""])
		return([True, ">>>>>>>>>>>>>>>>>>>Programmed flag order lock ON!", "987654321"])

	try:
		order = client.create_order(symbol           = symbOrd,
		                            quantity         = qtdOrd,
		                            price            = prcOrd,
		                            side             = sideOrd,
		                            type             = typeOrd,
		                            timeInForce      = Client.TIME_IN_FORCE_GTC,
		                            newOrderRespType = Client.ORDER_RESP_TYPE_FULL)

	except BinanceRequestException as e:
		return([False, f"Erro order_limit_buy BinanceRequestException: [{e.status_code} - {e.message}]", ""])
	except BinanceAPIException as e:
		return([False, f"Erro order_limit_buy BinanceAPIException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderException as e:
		return([False, f"Erro order_limit_buy BinanceOrderException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinAmountException as e:
		return([False, f"Erro order_limit_buy BinanceOrderMinAmountException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinPriceException as e:
		return([False, f"Erro order_limit_buy BinanceOrderMinPriceException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinTotalException as e:
		return([False, f"Erro order_limit_buy BinanceOrderMinTotalException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderUnknownSymbolException as e:
		return([False, f"Erro order_limit_buy BinanceOrderUnknownSymbolException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderInactiveSymbolException as e:
		return([False, f"Erro order_limit_buy BinanceOrderInactiveSymbolException: [{e.status_code} - {e.message}]", ""])
	except Exception as e:
		return([False, f"Erro order_limit_buy generic exception: {e}", ""])

	printPlacedOrder(order, log)

	return([True, "Ok", order['orderId']])

# ---------------------------------------------------

def buyOCOOrder(client, log = None, symb = '', qtd = 0, prc = 0.0, stopprice = 0.0, limit = 0.0) -> bool:
	log("NOT IMPLEMENTED")

def sellOCOOrder(client, log = None, symb = '', qtd = 0, prc = 0.0, stopprice = 0.0, limit = 0.0) -> bool:
	log("NOT IMPLEMENTED")

# ---------------------------------------------------

def orderMargin(client, log = None, symbOrd = '', sideOrd = 0, typeOrd = 0,
                qtdOrd = 0, prcOrd = 0.0, prcStop = 0.0, limit = 0.0) ->[bool, str, str]:
	log(f"MARGIN Order {typeOrd}")

	log(f"Symbol....: [{symbOrd}]")
	log(f"Side......: [{sideOrd}]")
	log(f"Quantity..: [{qtdOrd}]")
	log(f"Price.....: [{prcOrd}]")
	log(f"Stop Price: [{prcStop}]")
	log(f"Limit OCO.: [{limit}]")
	log(f"Type......: [{typeOrd}]")

	# TESTING
	global LOCK
	if LOCK == True:
		return([False, "Programmed flag order lock ON!", ""])

	try:
		if typeOrd == 'LIMIT':
			order = client.create_margin_order(symbol           = symbOrd,
		                                      side             = binanceSide(sideOrd),
		                                      type             = Client.ORDER_TYPE_LIMIT,
		                                      timeInForce      = Client.TIME_IN_FORCE_GTC,
		                                      quantity         = qtdOrd,
		                                      price            = prcOrd,
		                                      newOrderRespType = Client.ORDER_RESP_TYPE_FULL)
		else:
			order = client.create_margin_order(symbol           = symbOrd,
		                                      side             = binanceSide(sideOrd),
		                                      type             = BU.binanceOrderType(typeOrd),
		                                      timeInForce      = Client.TIME_IN_FORCE_GTC,
		                                      quantity         = qtdOrd,
		                                      price            = prcOrd,
		                                      stopPrice        = prcStop,
		                                      newOrderRespType = Client.ORDER_RESP_TYPE_FULL)

	except BinanceRequestException as e:
		return([False, f"Erro create_margin_order BinanceRequestException: [{e.status_code} - {e.message}]", ""])
	except BinanceAPIException as e:
		return([False, f"Erro create_margin_order BinanceAPIException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderException as e:
		return([False, f"Erro create_margin_order BinanceOrderException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinAmountException as e:
		return([False, f"Erro create_margin_order BinanceOrderMinAmountException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinPriceException as e:
		return([False, f"Erro create_margin_order BinanceOrderMinPriceException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderMinTotalException as e:
		return([False, f"Erro create_margin_order BinanceOrderMinTotalException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderUnknownSymbolException as e:
		return([False, f"Erro create_margin_order BinanceOrderUnknownSymbolException: [{e.status_code} - {e.message}]", ""])
	except BinanceOrderInactiveSymbolException as e:
		return([False, f"Erro create_margin_order BinanceOrderInactiveSymbolException: [{e.status_code} - {e.message}]", ""])
	except Exception as e:
		return([False, f"Erro create_margin_order generic exception: {e}", ""])

	log(f"\tOrder id....: [{order['orderId']}]")
	log(f"\tSymbol......: [{order['symbol']}]")
	log(f"\tPrice.......: [{order['price']}]")
	log(f"\tQtd.........: [{order['origQty']}]")
	log(f"\tQtd executed: [{order['executedQty']}]")
	log(f"\tSide........: [{order['side']}]")
	log(f"\tType........: [{order['type']}]")
	log(f"\tStop price..: [{order['stopPrice']}]")
	log(f"\tIs working..? [{order['isWorking']}]")

	return([True, "Ok", order['orderId']])
