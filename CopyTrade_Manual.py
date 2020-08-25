#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from os import getenv
from sys import exit, argv
from textwrap import fill
import configparser

import PySimpleGUI as sg
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException, BinanceRequestException

import BinanceCTDB
import BinanceCTOrder

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

def printAccountInfo(client)->[bool, str]:

	def printAccount(accBalance)->str:
		return f"Asset balance [{accBalance['asset']}] | Free [{accBalance['free']}] | Locked [{accBalance['locked']}]"

	def printMarginAssets(asset, seq = 0)->str:
		return f"{seq}) Asset: [{asset['asset']}]\n\tBorrowed.: [{asset['borrowed']}]\n\tFree.....: [{asset['free']}]\n\tLocked...: [{asset['locked']}]\n\tNet asset: [{asset['netAsset']}]\n"

	try:
		acc = client.get_account()
	except BinanceAPIException as e:
		return False, f"Erro at client.get_account() BinanceAPIException: [{e.status_code} - {e.message}]"
	except BinanceRequestException as e:
		return False, f"Erro at client.get_account() BinanceRequestException: [{e.status_code} - {e.message}]"
	except Exception as e:
		return False, f"Erro at client.get_account(): {e}"

	try:
		accStatus = client.get_account_status()
	except BinanceWithdrawException as e:
		return False, f"Erro at client.get_account_status() BinanceWithdrawException: [{e.status_code} - {e.message}]"
	except Exception as e:
		return False, f"Erro at client.get_account_status(): {e}"

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
		return False, f"Erro at client.get_margin_account() BinanceRequestException: [{e.status_code} - {e.message}]"
	except BinanceAPIException as e:
		return False, f"Erro at client.get_margin_account() BinanceAPIException: [{e.status_code} - {e.message}]"
	except Exception as e:
		return False, f"Erro at client.get_margin_account(): {e}"

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

	return True, "Ok"

def BS_MarginStopLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutMSL = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Stop Price: ', background_color = bgcolor), sg.InputText(key = '-STOP PRICE-')],
		[sg.Text('Limit Price: ', background_color = bgcolor), sg.InputText(key = '-LIMIT PRICE-')],
		[sg.Checkbox('send to CopyTrade', key='CB_COPYTRADE', default=True)],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowMSL = sg.Window(windowTitle, layoutMSL, background_color = bgcolor).Finalize()

	while True:
		eventMSL, valuesMSL = windowMSL.read()

		if eventMSL == 'SEND!':
			print(f"{windowTitle} - Order Symbol: [{valuesMSL['-SYMBOL-']}] Qtd: [{valuesMSL['-QTD-']}] Stop Prc: [{valuesMSL['-STOP PRICE-']}] Limit Prc: [{valuesMSL['-LIMIT PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				print(f'{windowTitle} - CANCELLED!')
				continue

			ret, retMsg = BinanceCTOrder.orderMargin(client,
			                             symbOrd = valuesMSL['-SYMBOL-'],
			                             qtdOrd = valuesMSL['-QTD-'],
			                             prcOrd = valuesMSL['-STOP PRICE-'],
			                             prcStop = valuesMSL['-LIMIT PRICE-'],
			                             sideOrd = clientSide,
			                             typeOrd = "TAKE_PROFIT_LIMIT",
			                             limit = 0.0 )
			if ret == False:
				sg.popup('ERRO! Order didnt post!')

				windowMSL.close()
				del windowMSL
				del layoutMSL

				return False, f"Erro posting order {retMsg}!"

			if valuesMSL['CB_COPYTRADE'] == True and COPYTRADE_IsEnable() == True:
				print(f"COPYTRADE: [MARGINSTOPLIMIT | TAKE_PROFIT_LIMIT | {valuesMSL['-SYMBOL-']} | {valuesMSL['-QTD-']} | {valuesMSL['-STOP PRICE-']} | {valuesMSL['-LIMIT PRICE-']} | {clientSide}]")

			print(f'{windowTitle} - CONFIRMED!')

		elif eventMSL == sg.WIN_CLOSED or eventMSL == 'CANCEL':
			print(f'{windowTitle} - CANCELLED!')
			break

	windowMSL.close()
	del windowMSL
	del layoutMSL

	return True, "Ok"

def BS_MarginMarket(client, bgcolor = '', windowTitle = '', clientSide = 0)-> bool:
	layoutMM = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Checkbox('send to CopyTrade', key='CB_COPYTRADE', default=True)],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowMM = sg.Window(windowTitle, layoutMM, background_color = bgcolor).Finalize()

	while True:
		eventMM, valuesMM = windowMM.read()

		if eventMM == 'SEND!':
			print(f"{windowTitle} - Order Symbol: [{valuesMM['-SYMBOL-']}] Qtd: [{valuesMM['-QTD-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				print(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet = BinanceCTOrder.orderMargin(client,
			                             symbOrd = valuesMM['-SYMBOL-'],
			                             qtdOrd  = valuesMM['-QTD-'],
			                             sideOrd = clientSide,
			                             typeOrd = Client.ORDER_TYPE_MARKET)
			if ret == False:
				sg.popup('ERRO! Order didnt post!')

				windowMM.close()
				del windowMM
				del layoutMM

				return False, f"Erro placing order! {msgRet}"

			if valuesMM['CB_COPYTRADE'] == True and COPYTRADE_IsEnable() == True:
				print("Call COPYTRADE...")

			print(f'{windowTitle} - CONFIRMED!')

		elif eventMM == sg.WIN_CLOSED or eventMM == 'CANCEL':
			print(f'{windowTitle} - CANCELLED!')
			break

	windowMM.close()

	del windowMM
	del layoutMM

	return True, "Ok"

def BS_MarginLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutML = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Price: ', background_color = bgcolor), sg.InputText(key = '-PRICE-')],
		[sg.Checkbox('send to CopyTrade', key='CB_COPYTRADE', default=True)],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowML = sg.Window(windowTitle, layoutML, background_color = bgcolor).Finalize()

	while True:
		eventML, valuesML = windowML.read()

		if eventML == 'SEND!':
			print(f"{windowTitle} - Order Symbol: [{valuesML['-SYMBOL-']}] Qtd: [{valuesML['-QTD-']}] Price: [{valuesML['-PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				print(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet = BinanceCTOrder.orderMargin(client,
			                  symbOrd = valuesML['-SYMBOL-'],
			                  qtdOrd  = valuesML['-QTD-'],
			                  prcOrd  = valuesML['-PRICE-'],
			                  sideOrd = clientSide,
			                  typeOrd = Client.ORDER_TYPE_LIMIT)

			if ret == False:
				sg.popup('ERRO! Order didnt post!')

				windowML.close()
				del windowML
				del layoutML

				return False, f"Eror posting order! {msgRet}"

			if valuesML['CB_COPYTRADE'] == True and COPYTRADE_IsEnable() == True:
				print("Call COPYTRADE...")

			print(f'{windowTitle} - CONFIRMED!')

		elif eventML == sg.WIN_CLOSED or eventML == 'CANCEL':
			print(f'{windowTitle} - CANCELLED!')
			break

	windowML.close()
	del windowML
	del layoutML

	return True, "Ok"

def BS_SpotStopLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[ bool, str]:
	layoutSSL = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Stop Price: ', background_color = bgcolor), sg.InputText(key = '-STOP PRICE-')],
		[sg.Text('Limit Price: ', background_color = bgcolor), sg.InputText(key = '-LIMIT PRICE-')],
		[sg.Checkbox('send to CopyTrade', key='CB_COPYTRADE', default=True)],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowSSL = sg.Window(windowTitle, layoutSSL, background_color = bgcolor).Finalize()

	while True:
		eventSSL, valuesSSL = windowSSL.read()

		if eventSSL == 'SEND!':
			print(f"{windowTitle} - Order Symbol: [{valuesSSL['-SYMBOL-']}] Qtd: [{valuesSSL['-QTD-']}] Stop Prc: [{valuesSSL['-STOP PRICE-']}] Limit Prc: [{valuesSSL['-LIMIT PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				print(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet = BinanceCTOrderO.orderSpotLimit(client,
			                                symbOrd = valuesSSL['-SYMBOL-'],
			                                qtdOrd = valuesSSL['-QTD-'],
			                                prcStopOrd = valuesSSL['-STOP PRICE-'],
			                                prcStopLimitOrd = valuesSSL['-LIMIT PRICE-'],
			                                sideOrd = clientSide)

			if ret == False:
				sg.popup('ERRO! Order didnt post!')

				windowSSL.close()
				del windowSSL
				del layoutSSL

				return False, f"Eror posting order! {msgRet}"

			if valuesSSL['CB_COPYTRADE'] == True and COPYTRADE_IsEnable() == True:
				print("Call COPYTRADE...")

			print(f'{windowTitle} - CONFIRMED!')

		elif eventSSL == sg.WIN_CLOSED or eventSSL == 'CANCEL':
			print(f'{windowTitle} - CANCELLED!')
			break

	windowSSL.close()
	del windowSSL
	del layoutSSL

	return True, "Ok"

def BS_SpotMarket(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutSM = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Checkbox('send to CopyTrade', key='CB_COPYTRADE', default=True)],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowSM = sg.Window(windowTitle, layoutSM, background_color = bgcolor).Finalize()

	while True:
		eventSM, valuesSM = windowSM.read()

		if eventSM == 'SEND!':
			print(f"{windowTitle} - Order Symbol: [{valuesSM['-SYMBOL-']}] Qtd: [{valuesSM['-QTD-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				print(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet = BinanceCTOrderO.orderSpot(client,
			                symbOrd = valuesSM['-SYMBOL-'],
			                qtdOrd  = valuesSM['-QTD-'],
			                sideOrd = clientSide,
			                typeOrd = Client.ORDER_TYPE_MARKET)
			if ret == False:
				sg.popup('ERRO! Order didnt post!')

				windowSM.close()
				del windowSM
				del layoutSM

				return False, f"Erro posting order! {msgRet}"

			if valuesSM['CB_COPYTRADE'] == True and COPYTRADE_IsEnable() == True:
				print("Call COPYTRADE...")

			print(f'{windowTitle} - CONFIRMED!')

		elif eventSM == sg.WIN_CLOSED or eventSM == 'CANCEL':
			print(f'{windowTitle} - CANCELLED!')
			break

	windowSM.close()

	del windowSM
	del layoutSM

	return True, "Ok"

def BS_SpotLimit(client, bgcolor = '', windowTitle = '', clientSide = 0)->[bool, str]:
	layoutSL = [
		[sg.Text('Symbol: ', background_color = bgcolor), sg.InputText(key = '-SYMBOL-')],
		[sg.Text('Qtd: ', background_color = bgcolor), sg.InputText(key = '-QTD-')],
		[sg.Text('Price: ', background_color = bgcolor), sg.InputText(key = '-PRICE-')],
		[sg.Checkbox('send to CopyTrade', key='CB_COPYTRADE', default=True)],
		[sg.Button('SEND!'), sg.Button('CANCEL')],
	]

	windowSL = sg.Window(windowTitle, layoutSL, background_color = bgcolor).Finalize()

	while True:
		eventSL, valuesSL = windowSL.read()

		if eventSL == 'SEND!':
			print(f"{windowTitle} - Order Symbol: [{valuesSL['-SYMBOL-']}] Qtd: [{valuesSL['-QTD-']}] Price: [{valuesSL['-PRICE-']}]")

			if sg.popup_yes_no('CONFIRM?', text_color='yellow', background_color='red') == 'No':
				print(f'{windowTitle} - CANCELLED!')
				continue

			ret, msgRet = BinanceCTOrder.orderSpot(client,
			                symbOrd = valuesSL['-SYMBOL-'],
			                qtdOrd  = valuesSL['-QTD-'],
			                prcOrd  = valuesSL['-PRICE-'],
			                sideOrd = clientSide,
			                typeOrd = Client.ORDER_TYPE_LIMIT)
			if ret == False:
				sg.popup('ERRO! Order didnt post!')

				windowSL.close()
				del windowSL
				del layoutSL

				return False, f"Erro posting order! {msgRet}"

			if valuesSL['CB_COPYTRADE'] == True and COPYTRADE_IsEnable() == True:
				print("Call COPYTRADE...")

			print(f'{windowTitle} - CONFIRMED!')

		elif eventSL == sg.WIN_CLOSED or eventSL == 'CANCEL':
			print(f'{windowTitle} - CANCELLED!')
			break

	windowSL.close()
	del windowSL
	del layoutSL

	return True, "Ok"

def ListOpenOrders(client)->[bool, str]:

	def buildOrderList(ordList):
		return [sg.CBox(f"{ordList['orderId']}", key=f"{ordList['orderId']}"),
		        sg.Text(f"{ordList['symbol']}\t\t{ordList['side']}\t\t{ordList['price']}\t\t{ordList['origQty']}\t\t{ordList['type']}", font=("Courier", 10))]

	try:
		openOrders = client.get_open_orders() #recvWindow
		openMarginOrders = client.get_open_margin_orders() #recvWindow
	except BinanceRequestException as e:
		return False, f"Erro at client.get_open_orders() BinanceRequestException: [{e.status_code} - {e.message}]"

	except BinanceAPIException as e:
		return False, f"Erro at client.get_open_orders() BinanceAPIException: [{e.status_code} - {e.message}]"

	except Exception as e:
		return False, f"Erro at client.get_open_orders(): {e}"

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
		print("Deleting margin orders:")

		for i in [str(k) for k, v in valuesLOO.items() if v == True]:

			for j2 in openMarginOrders:

				if j2['orderId'] == int(i):
					ret, msgRet = BinanceCTOrder.cancel_a_margin_order(client, symbOrd = j2['symbol'], ordrid = j2['orderId'])
					if ret == False:
						print(f"Erro canceling MARGIN order {j2['orderId']}! {msgRet}")

						windowListOpenOrder.close()

						del openOrders
						del openMarginOrders
						del windowListOpenOrder
						del layoutListOpenOrders

						return False, f"Erro canceling MARGIN order {j2['orderId']}! {msgRet}"

	elif eventLOO == 'Copy Margin data to clipboard':
		pass
	elif eventLOO == 'CopyTrade':
		pass

	elif eventLOO == 'Delete Spot Order':
		print("Deleting spot orders:")

		for i in [str(k) for k, v in valuesLOO.items() if v == True]:

			for j1 in openOrders:

				if j1['orderId'] == i:
					ret, msgRet = cancel_a_BO.spot_order(client, symbOrd = j2['symbol'], ordrid = j2['orderId'])
					if ret == False:
						print(f"Erro canceling SPOT order {j1['orderId']}! {msgRet}")

						windowListOpenOrder.close()

						del openOrders
						del openMarginOrders
						del windowListOpenOrder
						del layoutListOpenOrders

						return False, f"Erro canceling SPOT order {j1['orderId']}! {msgRet}"

	elif eventLOO == 'Copy Spot data to clipboard':
		pass
	elif eventLOO == 'CopyTrade':
		pass

	windowListOpenOrder.close()

	del openOrders
	del openMarginOrders
	del windowListOpenOrder
	del layoutListOpenOrders

	return True, 'Ok'

# --- CFG ---------------------------------

try:
	cfgFile = configparser.ConfigParser()
	cfgFile.read(argv[1])

	ctm_name = cfgFile['GENERAL']['name']
	ctm_log  = cfgFile['GENERAL']['log']
	ctm_enable  = cfgFile['GENERAL']['copytrade_enable']
	ctm_theme  = cfgFile['GENERAL']['theme']

	binance_apikey = cfgFile['BINANCE']['apikey']
	binance_sekkey = cfgFile['BINANCE']['sekkey']
	binance_recvwindow = cfgFile['BINANCE']['recvwindow']

	signalSource_port    = cfgFile['SIGNAL_SOURCE']['port']
	signalSource_address = cfgFile['SIGNAL_SOURCE']['address']

	db_engine = cfgFile['DB']['engine']

	if db_engine == BinanceCTDB.CT_DB_TYPE_SQLITE:
		db_file = cfgFile['DB']['file']

	elif db_engine == BinanceCTDB.CT_DB_TYPE_POSTGRESQL:
		db_user = cfgFile['DB']['user']
		db_pass = cfgFile['DB']['pass']
		db_port = cfgFile['DB']['port']
		db_schema = cfgFile['DB']['schema']

	else:
		print("Undefined DB engine config!", file=stderr)
		exit(1)

except Exception as e:
	print(f"Invalid cfg file! [{e}]")
	exit(1)

del cfgFile

# -----------------------------------------

STATUSBAR_WRAP = 100

menu = [
	[ '&Menu', ['Info', 'Config', '---', 'Read cfg', 'Write cfg', 'Create Empty Cfg file', '---', 'Exit']],
	[ '&Account', ['Infos acc', 'Taxes']],
	[ '&Order', ['BUY',  ['B Spot Market', 'B Spot Limit','B Spot Stop Limit', '!B Spot OCO', '---', 'B Margin Market', 'B Margin Limit', 'B Margin Stop Limit', '!B Margin OCO'],
	             'SELL', ['S Spot Market', 'S Spot Limit','S Spot Stop Limit', '!S Spot OCO', '---', 'S Margin Market', 'S Margin Limit', 'S Margin Stop Limit', '!S Margin OCO'], '!CANCEL', 'LIST or DELETE Open', '!LIST All']],
	[ '&Binance', ['Infos binance', 'Assets', 'Symbols']]
]

layout = [
	[sg.Menu(menu)],
	[sg.Button('Spot Market'      ,                key='BTTN_BSM' , button_color=('black','green'), size=(30,1)), sg.Button('Spot Market'      ,                key='BTTN_SSM' , button_color=('black', 'red'), size=(30,1))],
	[sg.Button('Spot Limit'       ,                key='BTTN_BSL' , button_color=('black','green'), size=(30,1)), sg.Button('Spot Limit'       ,                key='BTTN_SSL' , button_color=('black','red'), size=(30,1))],
	[sg.Button('Spot Stop Limit'  ,                key='BTTN_BSSL', button_color=('black','green'), size=(30,1)), sg.Button('Spot Stop Limit'  ,                key='BTTN_SSSL', button_color=('black','red'), size=(30,1))],
	[sg.Button('Spot OCO'         , disabled=True, key='BTTN_BSO' , button_color=('black','green'), size=(30,1)), sg.Button('Spot OCO'         , disabled=True, key='BTTN_SSO' , button_color=('black','red'), size=(30,1))],
	[sg.Button('Margin Market'    ,                key='BTTN_BMM' , button_color=('black','green'), size=(30,1)), sg.Button('Margin Market'    ,                key='BTTN_SMM' , button_color=('black','red'), size=(30,1))],
	[sg.Button('Margin Limit'     ,                key='BTTN_BML' , button_color=('black','green'), size=(30,1)), sg.Button('Margin Limit'     ,                key='BTTN_SML' , button_color=('black','red'), size=(30,1))],
	[sg.Button('Margin Stop Limit',                key='BTTN_BMSL', button_color=('black','green'), size=(30,1)), sg.Button('Margin Stop Limit',                key='BTTN_SMSL', button_color=('black','red'), size=(30,1))],
	[sg.Button('Margin OCO'       , disabled=True, key='BTTN_BMO' , button_color=('black','green'), size=(30,1)), sg.Button('Margin OCO'       , disabled=True, key='BTTN_SMO' , button_color=('black','red'), size=(30,1))],

	[sg.Button('LIST or DELETE Open Orders', key='BTTN_LDOO')],

	[sg.Button('CLOSE', key='BTTN_CLOSE')],
	[sg.StatusBar('Last msg: Initialized', key='LASTMSG', size=(250, 3), justification='left')],
]

#BU.setConfirmationYES(True)

# --- BINANCE CONNECTION ------------------
try:
	client = Client(binance_apikey, binance_sekkey, {"verify": True, "timeout": 20})

except BinanceAPIException as e:
	print(f"Binance API exception: [{e.status_code} - {e.message}]")
	exit(1)

except BinanceRequestException as e:
	print(f"Binance request exception: [{e.status_code} - {e.message}]")
	exit(1)

except BinanceWithdrawException as e:
	print(f"Binance withdraw exception: [{e.status_code} - {e.message}]")
	exit(1)

except Exception as e:
	print(f"Binance connection error: {e}")
	exit(1)

sg.theme(ctm_theme)

#sg.set_options(suppress_raise_key_errors=False, suppress_error_popups=False, suppress_key_guessing=False)

window = sg.Window('Binance Status GUI', layout, size = (600, 400)).Finalize()

while True:
	event, values = window.read()  #timeout=1000)

	if event == sg.WIN_CLOSED or event == 'Exit' or event == 'BTTN_CLOSE':
		break

	elif event == "Infos":
		sg.popup('INFOS')

	elif event == 'Info':
		pass

	elif event == 'Config':
		pass

	elif event == 'Infos acc':
		window.Hide()

		ret, msgRet = printAccountInfo(client)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	elif event == 'Taxes':
		pass

	# 'B Spot Market'
	elif event == 'BTTN_BSM':
		window.Hide()

		ret, msgRet = BS_SpotMarket(client, 'green', 'Buy Spot Market', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Spot Limit'
	elif event == 'BTTN_BSL':
		window.Hide()

		ret, msgRet = BS_SpotLimit(client, 'green', 'Buy Spot Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Spot Stop Limit'
	elif event == 'BTTN_BSSL':
		window.Hide()

		ret, msgRet = BS_SpotStopLimit(client, 'green', 'Buy Spot Stop Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Spot OCO'
	elif event == 'BTTN_BSO':
		pass

	# 'B Margin Market'
	elif event == 'BTTN_BMM':
		window.Hide()

		ret, msgRet = BS_MarginMarket(client, 'red', 'Sell Margin Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Margin Limit'
	elif event == 'BTTN_BML':
		window.Hide()

		ret, msgRet = BS_MarginLimit(client, 'green', 'Buy Margin Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Margin Stop Limit'
	elif event == 'BTTN_BMSL':
		window.Hide()

		ret, retMsg = BS_MarginStopLimit(client, 'green', 'Buy Margin Stop Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Margin OCO'
	elif event == 'BTTN_BMO':
		pass

	# 'S Spot Market'
	elif event == 'BTTN_SSM':
		window.Hide()

		ret, msgRet = BS_SpotMarket(client, 'red', 'Sell Spot Market', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Spot Limit'
	elif event == 'BTTN_SSL':
		window.Hide()

		ret, retMsg = BS_SpotLimit(client, 'red', 'Sell Spot Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Spot Stop Limit'
	elif event == 'BTTN_SSSL':
		window.Hide()

		ret, retMsg = BS_SpotStopLimit(client, 'red', 'Sell Spot Stop Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Spot OCO'
	elif event == 'BTTN_SSO':
		pass

	# 'S Margin Market'
	elif event == 'BTTN_SMM':
		window.Hide()

		ret, retMsg = BS_MarginMarket(client, 'red', 'Sell Margin Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Margin Limit'
	elif event == 'BTTN_SML':
		window.Hide()

		ret, retMsg = BS_MarginLimit(client, 'red', 'Sell Margin Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Margin Stop Limit'
	elif event == 'BTTN_SMSL':
		window.Hide()

		ret, msgRet = BS_MarginStopLimit(client, 'red', 'Sell Margin Stop Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Margin OCO'
	elif event == 'BTTN_SMO':
		pass

	elif event == 'CANCEL':
		pass

	# 'LIST or DELETE Open Orders'
	elif event == 'BTTN_LDOO':
		window.Hide()

		ret, msgRet = ListOpenOrders(client)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	elif event == 'LIST All':
		pass

	elif event == 'Infos binance':
		pass

	elif event == 'Assets':
		pass

	elif event == 'Symbols':
		pass

window.close()

exit(0)
