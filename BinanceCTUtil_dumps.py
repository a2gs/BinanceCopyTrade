#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

import BinanceCTProto

def dumpCmdReqToLog(dumpCmd : BinanceCTProto.CT_PROTO, log):
	log.debug(f"Command...........: {dumpCmd.cmd}")
	log.debug(f"From..............: {dumpCmd.fromto['from']}")
	log.debug(f"To................: {dumpCmd.fromto['to']}")
	log.debug(f"Type..............: {dumpCmd.cmdtype}")
	log.debug(f"Timestamp.........: {dumpCmd.timestamp}")
	log.debug(f"Response timestamp: {dumpCmd.resp_timestamp}")

	log.debug("Data:")

	if dumpCmd.cmd == BinanceCTProto.CT_CMD_COPYTRADE:

		if dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_RESPONSE:
			log.debug(f"\tReturn........: [{dumpCmd.data.ret}]")
			log.debug(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_REQUEST:
			log.debug(f"\tSymbol: [{dumpCmd.data.symbol}]")
			log.debug(f"\tSide..: [{dumpCmd.data.side}]")
			log.debug(f"\tId....: [{dumpCmd.data.ordid}]")
			log.debug(f"\tType..: [{dumpCmd.data.ordtype}]")
			log.debug(f"\tPrice.: [{dumpCmd.data.price}]")

		else:
			log.debug(f"Unknow data structure for this cmd type.")

	elif dumpCmd.cmd == BinanceCTProto.CT_CMD_PING:
		if dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_RESPONSE:
			log.debug(f"\tReturn........: [{dumpCmd.data.ret}]")
			log.debug(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_REQUEST:
			log.debug(f"\tTODO 1...")

		else:
			log.debug(f"Unknow data structure for this cmd type.")

	elif dumpCmd.cmd == BinanceCTProto.CT_CMD_CANCELORDER:
		if dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_RESPONSE:
			log.debug(f"\tReturn........: [{dumpCmd.data.ret}]")
			log.debug(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_REQUEST:
			log.debug(f"\tTODO 2...")

		else:
			log.debug(f"Unknow data structure for this cmd type.")

	elif dumpCmd.cmd == BinanceCTProto.CT_CMD_GETOPENORDERS:
		if dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_RESPONSE:
			log.debug(f"\tReturn........: [{dumpCmd.data.ret}]")
			log.debug(f"\tReturn message: [{dumpCmd.data.retmsg}]")

		elif dumpCmd.cmdtype == BinanceCTProto.CT_TYPE_REQUEST:
			log.debug(f"\tTODO 3...")

		else:
			log.debug(f"Unknow data structure for this cmd type.")

	else:
		log.debug(f"Unknow data structure for this cmd.")
