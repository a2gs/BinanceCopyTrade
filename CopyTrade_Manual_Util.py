#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

#from os import getenv, getpid
#from sys import exit, argv
#from textwrap import fill
#import configparser
import logging
import socket

import PySimpleGUI as sg
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException, BinanceRequestException

import envelop_sendRecv
import BinanceCTOrder
import BinanceCTProto
import BinanceCTUtil

class GUIUtilDefines:
	srvSendAddress = ""
	srvSendPort    = 0
	meName         = ""
	copytradeEnable = True

GUIUtilcfg = GUIUtilDefines()

def setCopyTradeEnable(n : bool = True):
	global GUIUtilcfg

	GUIUtilcfg.copytradeEnable = n

def getCopyTradeEnable():
	global GUIUtilcfg

	return(GUIUtilcfg.copytradeEnable)


def setSrvSendInformation(address : str = "", port : int = 0, me : str = ""):
	global GUIUtilcfg

	GUIUtilcfg.srvSendAddress = address
	GUIUtilcfg.srvSendPort    = port
	GUIUtilcfg.meName         = me

def sendOrderToSrvSend(symb : str = "",      side : str = "",
                       qtd : str = "",       price : str = "",
                       priceStop : str = "", priceLimit : str = "",
                       typeOrd : str = "",   orderCTId : str = "")->[bool, str]:
	global GUIUtilcfg

	orderToSendData = BinanceCTProto.CT_PROTO_COPYTRADE_DATA(_symbol     = symb,
	                                                         _side       = side,
	                                                         _qtd        = qtd,
	                                                         _ordid      = orderCTId,
	                                                         _ordtype    = typeOrd,
	                                                         _price      = price,
	                                                         _priceStop  = priceStop,
	                                                         _priceLimit = priceLimit)

	orderToSend = BinanceCTProto.CT_PROTO(_cmd            = BinanceCTProto.CT_CMD_COPYTRADE,
	                                      _fromto_from    = GUIUtilcfg.meName,
	                                      _fromto_to      = "SrvSend",
	                                      _timestamp      = BinanceCTUtil.getTimeStamp(),
	                                      _cmdtype        = BinanceCTProto.CT_TYPE_REQUEST,
	                                      _resp_timestamp = "",
	                                      _data           = orderToSendData)

	ret, msg = orderToSend.formatToNet()
	if ret == False:
		return([False, msg])

	con = envelop_sendRecv.connection()

	logging.debug(f"Connecting to SrvSend: {GUIUtilcfg.srvSendAddress} {GUIUtilcfg.srvSendPort}")
	ret, retmsg = con.connectToServer(GUIUtilcfg.srvSendAddress, GUIUtilcfg.srvSendPort, socket.AF_INET, socket.SOCK_STREAM)
	if ret == False:
		return([False, f"Connect to server error: {retmsg}"])

	ret, retmsg = con.sendMsg(msg, len(msg))
	if ret == False:
		return([False, f"Send to server error: {retmsg}"])

	ret, retmsg, msgRecv = con.recvMsg()
	if ret == False:
		return([False, f"Error msgRecv: [{retmsg}]"])

	orderRecv = BinanceCTProto.CT_PROTO()
	orderRecv.loadFromNet(msgRecv)

	logging.info(f'Sent: [{msg}]')
	BinanceCTProto.dumpCmdToLog(orderToSend, logging.info)

	logging.info(f'Received: [{msgRecv}]')
	BinanceCTProto.dumpCmdToLog(orderRecv, logging.info)

	return([True, "Ok"])

def printAccountInfo(client)->[bool, str]:

	def printAccount(accBalance)->str:
		return f"Asset balance [{accBalance['asset']}] | Free [{accBalance['free']}] | Locked [{accBalance['locked']}]"

	def printMarginAssets(asset, seq = 0)->str:
		return f"{seq}) Asset: [{asset['asset']}]\n\tBorrowed.: [{asset['borrowed']}]\n\tFree.....: [{asset['free']}]\n\tLocked...: [{asset['locked']}]\n\tNet asset: [{asset['netAsset']}]\n"

	try:
		acc = client.get_account()
	except BinanceAPIException as e:
		return([False, f"Erro at client.get_account() BinanceAPIException: [{e.status_code} - {e.message}]"])
	except BinanceRequestException as e:
		return([False, f"Erro at client.get_account() BinanceRequestException: [{e.status_code} - {e.message}]"])
	except Exception as e:
		return([False, f"Erro at client.get_account(): {e}"])

	try:
		accStatus = client.get_account_status()
	except BinanceWithdrawException as e:
		return([False, f"Erro at client.get_account_status() BinanceWithdrawException: [{e.status_code} - {e.message}]"])
	except Exception as e:
		return([False, f"Erro at client.get_account_status(): {e}"])

	totalinfos = f"Can trade............? [{acc['canTrade']}]\n"
	totalinfos += f"Can withdraw.........? [{acc['canWithdraw']}]\n"
	totalinfos += f"Can deposit..........? [{acc['canDeposit']}]\n"
	totalinfos += f"Account type.........: [{acc['accountType']}]\n"
	totalinfos += f"Account status detail: [{accStatus['msg']}] Success: [{accStatus['success']}]\n"
	totalinfos += f"Commissions..........: Maker: [{acc['makerCommission']}] | Taker: [{acc['takerCommission']}] | Buyer: [{acc['buyerCommission']}] | Seller: [{acc['sellerCommission']}]\n\n"

	totalinfos += "Balances:\n"
	if len(acc['balances']) != 0:
		totalinfos += '\n'.join([printAccount(n) for n in acc['balances'] if float(n['free']) != 0.0 or float(n['locked']) != 0.0]) + '\n\n'
	else:
		totalinfos += 'Zero.\n\n'

	totalinfos += "Margin accoutn information:\n"
	try:
		marginInfo = client.get_margin_account()
	except BinanceRequestException as e:
		return([False, f"Erro at client.get_margin_account() BinanceRequestException: [{e.status_code} - {e.message}]"])
	except BinanceAPIException as e:
		return([False, f"Erro at client.get_margin_account() BinanceAPIException: [{e.status_code} - {e.message}]"])
	except Exception as e:
		return([False, f"Erro at client.get_margin_account(): {e}"])

	cleanedMarginAssets = [n for n in marginInfo['userAssets'] if float(n['netAsset']) != 0.0]

	totalinfos += f"Borrow Enabled........? [{marginInfo['borrowEnabled']}]\n"
	totalinfos += f"Trade enabled.........? [{marginInfo['tradeEnabled']}]\n"
	totalinfos += f"Level.................: [{marginInfo['marginLevel']}]\n"
	totalinfos += f"Total asset of BTC....: [{marginInfo['totalAssetOfBtc']}]\n"
	totalinfos += f"Total liability of BTC: [{marginInfo['totalLiabilityOfBtc']}]\n"
	totalinfos += f"Total Net asset of BTC: [{marginInfo['totalNetAssetOfBtc']}]\n\n"

	totalinfos += 'Borrowed assets:\n'
	totalinfos += '\n'.join ([printMarginAssets(n, i) for i, n in enumerate(cleanedMarginAssets, 1)])

	layoutAccInfo = [[sg.Multiline(totalinfos, key='-INFOMLINE-' + sg.WRITE_ONLY_KEY, size=(100,25), font='Courier 10', disabled=True)], [sg.Button('Ok')]]

	windowInfoAcc = sg.Window("Acc Infos", layoutAccInfo).Finalize()
	eventInfoAcc, valuesInfoAcc = windowInfoAcc.read()

	windowInfoAcc.close()

	del totalinfos
	del acc
	del accStatus
	del marginInfo
	del cleanedMarginAssets
	del windowInfoAcc
	del layoutAccInfo

	return([True, "Ok"])

def BS_MarginStopLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutMSL = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Stop Price: ', background_color = bgcolor), sg.InputText(key = '-STOP PRICE-')],
		[sg.Text('Limit Price: ', background_color = bgcolor), sg.InputText(key = '-LIMIT PRICE-')],
		[sg.Checkbox('Send to CopyTrade', key='CB_COPYTRADE', default=True, disabled=not getCopyTradeEnable())],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowMSL = sg.Window(windowTitle, layoutMSL, background_color = bgcolor).Finalize()

	while True:
		eventMSL, valuesMSL = windowMSL.read()

		if eventMSL == 'SEND!':
			logging.info(f"{windowTitle} - Order Symbol: [{valuesMSL['-SYMBOL-']}] Qtd: [{valuesMSL['-QTD-']}] Stop Prc: [{valuesMSL['-STOP PRICE-']}] Limit Prc: [{valuesMSL['-LIMIT PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				logging.info(f'{windowTitle} - CANCELLED!')
				continue

			ret, retMsg, orderId = BinanceCTOrder.orderMargin(client,
			                                                  logging.info,
			                                                  symbOrd = valuesMSL['-SYMBOL-'],
			                                                  qtdOrd = valuesMSL['-QTD-'],
			                                                  prcOrd = valuesMSL['-STOP PRICE-'],
			                                                  prcStop = valuesMSL['-LIMIT PRICE-'],
			                                                  sideOrd = clientSide,
			                                                  typeOrd = "TAKE_PROFIT_LIMIT",
			                                                  limit = 0.0 )

			if ret == False:
				logging.info(f"Erro posting order! {msgRet}")
				sg.popup('ERRO! Order didnt post!')

				windowMSL.close()
				del windowMSL
				del layoutMSL

				return([False, f"Erro posting order {retMsg}!"])

			if valuesMSL['CB_COPYTRADE'] == True:
				ret, retmsg = sendOrderToSrvSend(symb = valuesMSL['-SYMBOL-'],
				                                 side = clientSide,
				                                 qtd = valuesMSL['-QTD-'],
				                                 price = "0.0",
				                                 priceStop = valuesMSL['-LIMIT PRICE-'],
				                                 priceLimit = "0.0",
				                                 typeOrd = "TAKE_PROFIT_LIMIT",
				                                 orderCTId = orderId)
				if ret == False:
					logging.warning(f"The Order ID could not be sent to SrvSend [{orderId}] [{retmsg}]!")

			logging.info(f'{windowTitle} - CONFIRMED!')
			break

		elif eventMSL == sg.WIN_CLOSED or eventMSL == 'CANCEL':
			logging.info(f'{windowTitle} - CANCELLED!')
			break

	windowMSL.close()
	del windowMSL
	del layoutMSL

	return([True, "Ok"])

def BS_MarginMarket(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutMM = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Checkbox('Send to CopyTrade', key='CB_COPYTRADE', default=True, disabled=not getCopyTradeEnable())],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowMM = sg.Window(windowTitle, layoutMM, background_color = bgcolor).Finalize()

	while True:
		eventMM, valuesMM = windowMM.read()

		if eventMM == 'SEND!':
			logging.info(f"{windowTitle} - Order Symbol: [{valuesMM['-SYMBOL-']}] Qtd: [{valuesMM['-QTD-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				logging.info(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet, orderId = BinanceCTOrder.orderMargin(client,
			                                                  logging.info,
			                                                  symbOrd = valuesMM['-SYMBOL-'],
			                                                  qtdOrd  = valuesMM['-QTD-'],
			                                                  sideOrd = clientSide,
			                                                  typeOrd = Client.ORDER_TYPE_MARKET)
			if ret == False:
				logging.info(f"Erro posting order! {msgRet}")
				sg.popup('ERRO! Order didnt post!')

				windowMM.close()
				del windowMM
				del layoutMM

				return([False, f"Erro placing order! {msgRet}"])

			if valuesMM['CB_COPYTRADE'] == True:
				ret, retmsg = sendOrderToSrvSend(symb = valuesMM['-SYMBOL-'],
				                                 side = clientSide,
				                                 qtd = valuesMM['-QTD-'],
				                                 typeOrd = Client.ORDER_TYPE_MARKET,
				                                 orderCTId = clientSide)
				if ret == False:
					logging.warning(f"The Order ID could not be sent to SrvSend [{orderId}] [{retmsg}]!")

			logging.info(f'{windowTitle} - CONFIRMED!')
			break

		elif eventMM == sg.WIN_CLOSED or eventMM == 'CANCEL':
			logging.info(f'{windowTitle} - CANCELLED!')
			break

	windowMM.close()

	del windowMM
	del layoutMM

	return([True, "Ok"])

def BS_MarginLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutML = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Price: ', background_color = bgcolor), sg.InputText(key = '-PRICE-')],
		[sg.Checkbox('Send to CopyTrade', key='CB_COPYTRADE', default=True, disabled=not getCopyTradeEnable())],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowML = sg.Window(windowTitle, layoutML, background_color = bgcolor).Finalize()

	while True:
		eventML, valuesML = windowML.read()

		if eventML == 'SEND!':
			logging.info(f"{windowTitle} - Order Symbol: [{valuesML['-SYMBOL-']}] Qtd: [{valuesML['-QTD-']}] Price: [{valuesML['-PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				logging.info(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet, orderId = BinanceCTOrder.orderMargin(client,
			                                                  logging.info,
			                                                  symbOrd = valuesML['-SYMBOL-'],
			                                                  qtdOrd  = valuesML['-QTD-'],
			                                                  prcOrd  = valuesML['-PRICE-'],
			                                                  sideOrd = clientSide,
			                                                  typeOrd = Client.ORDER_TYPE_LIMIT)

			if ret == False:
				logging.info(f"Erro posting order! {msgRet}")
				sg.popup('ERRO! Order didnt post!')

				windowML.close()
				del windowML
				del layoutML

				return([False, f"Eror posting order! {msgRet}"])

			if valuesML['CB_COPYTRADE'] == True:
				ret, retmsg = sendOrderToSrvSend(symb = valuesML['-SYMBOL-'],
				                                 side = clientSide,
				                                 qtd = valuesML['-QTD-'],
				                                 price = valuesML['-PRICE-'],
				                                 typeOrd = Client.ORDER_TYPE_LIMIT,
				                                 orderCTId = orderId)
				if ret == False:
					logging.warning(f"The Order ID could not be sent to SrvSend [{orderId}] [{retmsg}]!")

			logging.info(f'{windowTitle} - CONFIRMED!')
			break

		elif eventML == sg.WIN_CLOSED or eventML == 'CANCEL':
			logging.info(f'{windowTitle} - CANCELLED!')
			break

	windowML.close()
	del windowML
	del layoutML

	return([True, "Ok"])

def BS_SpotStopLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutSSL = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Stop Price: ', background_color = bgcolor), sg.InputText(key = '-STOP PRICE-')],
		[sg.Text('Limit Price: ', background_color = bgcolor), sg.InputText(key = '-LIMIT PRICE-')],
		[sg.Checkbox('Send to CopyTrade', key='CB_COPYTRADE', default=True, disabled=not getCopyTradeEnable())],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowSSL = sg.Window(windowTitle, layoutSSL, background_color = bgcolor).Finalize()

	while True:
		eventSSL, valuesSSL = windowSSL.read()

		if eventSSL == 'SEND!':
			logging.info(f"{windowTitle} - Order Symbol: [{valuesSSL['-SYMBOL-']}] Qtd: [{valuesSSL['-QTD-']}] Stop Prc: [{valuesSSL['-STOP PRICE-']}] Limit Prc: [{valuesSSL['-LIMIT PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				logging.info(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet = BinanceCTOrder.orderSpotLimit(client,
			                                            logging.info,
			                                            symbOrd = valuesSSL['-SYMBOL-'],
			                                            qtdOrd = valuesSSL['-QTD-'],
			                                            prcStopOrd = valuesSSL['-STOP PRICE-'],
			                                            prcStopLimitOrd = valuesSSL['-LIMIT PRICE-'],
			                                            sideOrd = clientSide)

			if ret == False:
				logging.info(f"Erro posting order! {msgRet}")
				sg.popup('ERRO! Order didnt post!')

				windowSSL.close()
				del windowSSL
				del layoutSSL

				return([False, f"Eror posting order! {msgRet}"])

			if valuesSSL['CB_COPYTRADE'] == True:
				ret, retmsg = sendOrderToSrvSend(symb = valuesSSL['-SYMBOL-'],
				                                 side = clientSide,
				                                 qtd = valuesSSL['-QTD-'],
				                                 price = "",
				                                 priceStop = valuesSSL['-STOP PRICE-'],
				                                 priceLimit = valuesSSL['-LIMIT PRICE-'],
				                                 typeOrd = ">>>SPOT LIMIT",
				                                 orderCTId = orderId)
				if ret == False:
					logging.warning(f"The Order ID could not be sent to SrvSend [{orderId}] [{retmsg}]!")

			logging.info(f'{windowTitle} - CONFIRMED!')
			break

		elif eventSSL == sg.WIN_CLOSED or eventSSL == 'CANCEL':
			logging.info(f'{windowTitle} - CANCELLED!')
			break

	windowSSL.close()
	del windowSSL
	del layoutSSL

	return([True, "Ok"])

def BS_SpotMarket(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutSM = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Checkbox('Send to CopyTrade', key='CB_COPYTRADE', default=True, disabled=not getCopyTradeEnable())],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowSM = sg.Window(windowTitle, layoutSM, background_color = bgcolor).Finalize()

	while True:
		eventSM, valuesSM = windowSM.read()

		if eventSM == 'SEND!':
			logging.info(f"{windowTitle} - Order Symbol: [{valuesSM['-SYMBOL-']}] Qtd: [{valuesSM['-QTD-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				logging.info(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet, orderId = BinanceCTOrder.orderSpot(client,
			                                                logging.info,
			                                                symbOrd = valuesSM['-SYMBOL-'],
			                                                qtdOrd  = valuesSM['-QTD-'],
			                                                sideOrd = clientSide,
			                                                typeOrd = Client.ORDER_TYPE_MARKET)
			if ret == False:
				logging.info(f"Erro posting order! {msgRet}")
				sg.popup('ERRO! Order didnt post!')

				windowSM.close()
				del windowSM
				del layoutSM

				return([False, f"Erro posting order! {msgRet}"])

			if valuesSM['CB_COPYTRADE'] == True:
				ret, retmsg = sendOrderToSrvSend(symb = valuesSM['-SYMBOL-'],
				                                 side = clientSide,
				                                 qtd = valuesSM['-QTD-'],
				                                 typeOrd = Client.ORDER_TYPE_MARKET,
				                                 orderCTId = orderId)
				if ret == False:
					logging.warning(f"The Order ID could not be sent to SrvSend [{orderId}] [{retmsg}]!")

			logging.info(f'{windowTitle} - CONFIRMED!')
			break

		elif eventSM == sg.WIN_CLOSED or eventSM == 'CANCEL':
			logging.info(f'{windowTitle} - CANCELLED!')
			break

	windowSM.close()

	del windowSM
	del layoutSM

	return([True, "Ok"])

def BS_SpotLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutSL = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Price: ', background_color = bgcolor), sg.InputText(key = '-PRICE-')],
		[sg.Checkbox('Send to CopyTrade', key='CB_COPYTRADE', default=True, disabled=not getCopyTradeEnable())],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowSL = sg.Window(windowTitle, layoutSL, background_color = bgcolor).Finalize()

	while True:
		eventSL, valuesSL = windowSL.read()

		if eventSL == 'SEND!':
			logging.info(f"{windowTitle} - Order Symbol: [{valuesSL['-SYMBOL-']}] Qtd: [{valuesSL['-QTD-']}] Price: [{valuesSL['-PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				logging.info(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet, orderId = BinanceCTOrder.orderSpot(client,
			                                                logging.info,
			                                                symbOrd = valuesSL['-SYMBOL-'],
			                                                qtdOrd  = valuesSL['-QTD-'],
			                                                prcOrd  = valuesSL['-PRICE-'],
			                                                sideOrd = clientSide,
			                                                typeOrd = Client.ORDER_TYPE_LIMIT)
			if ret == False:
				logging.info(f"Erro posting order! {msgRet}")
				sg.popup('ERRO! Order didnt post!')

				windowSL.close()
				del windowSL
				del layoutSL

				return([False, f"Erro posting order! {msgRet}"])

			if valuesSL['CB_COPYTRADE'] == True:
				ret, retmsg = sendOrderToSrvSend(symb = valuesSL['-SYMBOL-'],
				                                 side = clientSide,
				                                 qtd = valuesSL['-QTD-'],
				                                 price = valuesSL['-PRICE-'],
				                                 typeOrd = Client.ORDER_TYPE_LIMIT,
				                                 orderCTId = orderId)
				if ret == False:
					logging.warning(f"The Order ID could not be sent to SrvSend [{orderId}] [{retmsg}]!")

			logging.info(f'{windowTitle} - CONFIRMED!')
			break

		elif eventSL == sg.WIN_CLOSED or eventSL == 'CANCEL':
			logging.info(f'{windowTitle} - CANCELLED!')
			break

	windowSL.close()
	del windowSL
	del layoutSL

	return([True, "Ok"])

def ListOpenOrders(client)->[bool, str]:

	def buildOrderList(ordList):
		return([sg.CBox(f"{ordList['orderId']}", key=f"{ordList['orderId']}"),
		        sg.Text(f"{ordList['symbol']}\t\t{ordList['side']}\t\t{ordList['price']}\t\t{ordList['origQty']}\t\t{ordList['type']}", font=("Courier", 10))])

	try:
		openOrders = client.get_open_orders() #recvWindow
		openMarginOrders = client.get_open_margin_orders() #recvWindow
	except BinanceRequestException as e:
		return([False, f"Erro at client.get_open_orders() BinanceRequestException: [{e.status_code} - {e.message}]"])

	except BinanceAPIException as e:
		return([False, f"Erro at client.get_open_orders() BinanceAPIException: [{e.status_code} - {e.message}]"])

	except Exception as e:
		return([False, f"Erro at client.get_open_orders(): {e}"])

	if len(openOrders) == 0:
		layoutFrameSpotOpen = [[sg.Text("0 orders.", font=("Courier", 10))]]
	else:
		layoutFrameSpotOpen = [[sg.Text("Order Id\tSymbol\tSide\tPrice\tQtd\tType", font=("Courier", 10))]]
		[layoutFrameSpotOpen.append(buildOrderList(i)) for i in openOrders]
		layoutFrameSpotOpen.append([sg.Button('Delete Spot Order'), sg.Button('Copy Spot data to clipboard'), sg.Button('CopyTrade')])

	if len(openMarginOrders) == 0:
		layoutFrameMarginOpen = [[sg.Text("0 orders.", font=("Courier", 10))]]
	else:
		layoutFrameMarginOpen = [[sg.Text("Order Id\tSymbol\tSide\tPrice\tQtd\tType", font=("Courier", 10))]]
		[layoutFrameMarginOpen.append(buildOrderList(i)) for i in openMarginOrders]
		layoutFrameMarginOpen.append([sg.Button('Delete Margin Order'), sg.Button('Copy Margin data to clipboard'), sg.Button('CopyTrade')])

	layoutListOpenOrders = [
		[sg.Frame('SPOT', layoutFrameSpotOpen, title_color='blue')],
		[sg.Frame('MARGIN', layoutFrameMarginOpen, title_color='blue')],
		[sg.Button('Close')]
	]

	windowListOpenOrder = sg.Window('Open Orders', layoutListOpenOrders);

	eventLOO, valuesLOO = windowListOpenOrder.read()

	del layoutFrameSpotOpen
	del layoutFrameMarginOpen

	if eventLOO == sg.WIN_CLOSED or eventLOO == 'Close':
		pass

	elif eventLOO == 'Delete Margin Order':
		logging.info("Deleting margin orders:")

		for i in [str(k) for k, v in valuesLOO.items() if v == True]:

			for j2 in openMarginOrders:

				if j2['orderId'] == int(i):
					ret, msgRet = BinanceCTOrder.cancel_a_margin_order(client, logging.info, symbOrd = j2['symbol'], ordrid = j2['orderId'])
					if ret == False:
						logging.info(f"Erro canceling MARGIN order {j2['orderId']}! {msgRet}")

						windowListOpenOrder.close()

						del openOrders
						del openMarginOrders
						del windowListOpenOrder
						del layoutListOpenOrders

						return([False, f"Erro canceling MARGIN order {j2['orderId']}! {msgRet}"])

	elif eventLOO == 'Copy Margin data to clipboard':
		pass
	elif eventLOO == 'CopyTrade':
		pass

	elif eventLOO == 'Delete Spot Order':
		logging.info("Deleting spot orders:")

		for i in [str(k) for k, v in valuesLOO.items() if v == True]:

			for j1 in openOrders:

				if j1['orderId'] == i:
					ret, msgRet = BinanceCTOrder.cancel_a_spot_order(client, logging.info, symbOrd = j2['symbol'], ordrid = j2['orderId'])
					if ret == False:
						logging.info(f"Erro canceling SPOT order {j1['orderId']}! {msgRet}")

						windowListOpenOrder.close()

						del openOrders
						del openMarginOrders
						del windowListOpenOrder
						del layoutListOpenOrders

						return([False, f"Erro canceling SPOT order {j1['orderId']}! {msgRet}"])

	elif eventLOO == 'Copy Spot data to clipboard':
		pass
	elif eventLOO == 'CopyTrade':
		pass

	windowListOpenOrder.close()

	del openOrders
	del openMarginOrders
	del windowListOpenOrder
	del layoutListOpenOrders

	return([True, 'Ok'])
