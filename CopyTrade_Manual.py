#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from os import getenv, getpid
from sys import exit, argv
from textwrap import fill
import configparser
import logging

import PySimpleGUI as sg
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException, BinanceRequestException

import BinanceCTDB
import BinanceCTUtil
import CopyTrade_Manual_Util

if len(argv) != 2:
	print(f"Usage:\n\t{argv[0]} CFG_FILE.cfg")
	exit(1)

con   = None # Socket: signal source
ctmDB = None # Database handle

def safeExit(num : int = 0, msg : str = ""):

	if ctmDB is not None:
		ctmDB.DB.commit()
		ctmDB.DB.quit()

	if msg != "":
		logging.info(msg)

	logging.info(f"Exit with code [{num}]")
	exit(num)

# --- CFG ---------------------------------

try:
	cfgFile = configparser.ConfigParser()
	cfgFile.read(argv[1])

	ctm_name   = cfgFile['GENERAL']['name']
	ctm_log    = cfgFile['GENERAL']['log']
	ctm_enable = cfgFile['GENERAL']['copytrade_enable']
	ctm_theme  = cfgFile['GENERAL']['theme']

	binance_apikey     = cfgFile['BINANCE']['apikey']
	binance_sekkey     = cfgFile['BINANCE']['sekkey']
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

# --- LOG ---------------------------------

try:
	logging.basicConfig(filename = ctm_log,
	                    level    = logging.INFO,
	                    format   = '%(asctime)s %(message)s',
	                    datefmt  = '%Y%m%d %H%M%S')
except:
	print(f"Erro open log file: [{pub_log}]", file=stderr)
	exit(1)

# --- PRINT CFG ---------------------------

logging.info(f"Starting at: [{BinanceCTUtil.getTimeStamp()}] PID: [{getpid()}]")

logging.info('Configuration:')
logging.info(f"Name.....................: [{ctm_name}]")
logging.info(f"Copy Trade enable........? [{ctm_enable}]")
logging.info(f"Theme....................: [{ctm_theme}]")

logging.info(f"Signal Send port.........: [{signalSource_port}]")
logging.info(f"Signal Send address......: [{signalSource_address}]")

logging.info(f"Binance API..............: [{binance_apikey}]")
logging.info(f"Binance Recv windows.....: [{binance_recvwindow}]")

logging.info(f"DB Engine................: [{db_engine}]")

if db_engine == BinanceCTDB.CT_DB_TYPE_SQLITE:
	logging.info(f"DB File..................: [{db_file}]")

elif db_engine == BinanceCTDB.CT_DB_TYPE_POSTGRESQL:
	logging.info(f"DB User..................: [{db_user}]")
	logging.info(f"DB Port..................: [{db_port}]")
	logging.info(f"DB Schema................: [{db_schema}]")

# --- BINANCE CONNECTION ------------------

try:
	client = Client(binance_apikey, binance_sekkey, {"verify": True, "timeout": 20})

except BinanceAPIException as e:
	safeExit(1, f"Binance API exception: [{e.status_code} - {e.message}]")

except BinanceRequestException as e:
	safeExit(1, f"Binance request exception: [{e.status_code} - {e.message}]")

except BinanceWithdrawException as e:
	safeExit(1, f"Binance withdraw exception: [{e.status_code} - {e.message}]")

except Exception as e:
	safeExit(1, f"Binance connection error: {e}")

# --- DATABASE ----------------------------

ctmDB = BinanceCTDB.CT_DB(_engine = db_engine, _sqliteDBFile = db_file)

ret, retmsg = ctmDB.DB.connect()
if ret == False:
	logging.info(f"Error opening database: [{retmsg}]")
	exit(1)

ret, retmsg = ctmDB.DB.createTablesIfNotExist()
if ret == False:
	safeExit(1, f"Error creating tables: [{retmsg}]")

# -----------------------------------------

if ctm_enable == "YES":
	CopyTrade_Manual_Util.setCopyTradeEnable(True)
else:
	CopyTrade_Manual_Util.setCopyTradeEnable(False)
	loggging.info("Copy trade disable by config file")

CopyTrade_Manual_Util.setSrvSendInformation(signalSource_address, int(signalSource_port), ctm_name)

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

		ret, msgRet = CopyTrade_Manual_Util.printAccountInfo(client)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	elif event == 'Taxes':
		pass

	# 'B Spot Market'
	elif event == 'BTTN_BSM':
		window.Hide()

		ret, msgRet = CopyTrade_Manual_Util.BS_SpotMarket(client, 'green', 'Buy Spot Market', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Spot Limit'
	elif event == 'BTTN_BSL':
		window.Hide()

		ret, msgRet = CopyTrade_Manual_Util.BS_SpotLimit(client, 'green', 'Buy Spot Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Spot Stop Limit'
	elif event == 'BTTN_BSSL':
		window.Hide()

		ret, msgRet = CopyTrade_Manual_Util.BS_SpotStopLimit(client, 'green', 'Buy Spot Stop Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Spot OCO'
	elif event == 'BTTN_BSO':
		pass

	# 'B Margin Market'
	elif event == 'BTTN_BMM':
		window.Hide()

		ret, msgRet = CopyTrade_Manual_Util.BS_MarginMarket(client, 'red', 'Sell Margin Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Margin Limit'
	elif event == 'BTTN_BML':
		window.Hide()

		ret, msgRet = CopyTrade_Manual_Util.BS_MarginLimit(client, 'green', 'Buy Margin Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Margin Stop Limit'
	elif event == 'BTTN_BMSL':
		window.Hide()

		ret, retMsg = CopyTrade_Manual_Util.BS_MarginStopLimit(client, 'green', 'Buy Margin Stop Limit', Client.SIDE_BUY)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'B Margin OCO'
	elif event == 'BTTN_BMO':
		pass

	# 'S Spot Market'
	elif event == 'BTTN_SSM':
		window.Hide()

		ret, msgRet = CopyTrade_Manual_Util.BS_SpotMarket(client, 'red', 'Sell Spot Market', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {msgRet}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Spot Limit'
	elif event == 'BTTN_SSL':
		window.Hide()

		ret, retMsg = CopyTrade_Manual_Util.BS_SpotLimit(client, 'red', 'Sell Spot Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Spot Stop Limit'
	elif event == 'BTTN_SSSL':
		window.Hide()

		ret, retMsg = CopyTrade_Manual_Util.BS_SpotStopLimit(client, 'red', 'Sell Spot Stop Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Spot OCO'
	elif event == 'BTTN_SSO':
		pass

	# 'S Margin Market'
	elif event == 'BTTN_SMM':
		window.Hide()

		ret, retMsg = CopyTrade_Manual_Util.BS_MarginMarket(client, 'red', 'Sell Margin Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Margin Limit'
	elif event == 'BTTN_SML':
		window.Hide()

		ret, retMsg = CopyTrade_Manual_Util.BS_MarginLimit(client, 'red', 'Sell Margin Limit', Client.SIDE_SELL)
		window['LASTMSG'].update(fill(f'Last operation returned: {retMsg}', STATUSBAR_WRAP))

		window.UnHide()

	# 'S Margin Stop Limit'
	elif event == 'BTTN_SMSL':
		window.Hide()

		ret, msgRet = CopyTrade_Manual_Util.BS_MarginStopLimit(client, 'red', 'Sell Margin Stop Limit', Client.SIDE_SELL)
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

		ret, msgRet = CopyTrade_Manual_Util.ListOpenOrders(client)
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

safeExit(0)
