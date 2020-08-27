#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

# i hate python for force me to import this module for a descent class interface, from all of my heart.
import abc

import sqlite3
#import psycopg2

import BinanceCTProto

CT_DB_TYPE_SQLITE     = "sqlite"
CT_DB_TYPE_POSTGRESQL = "postgresql"
CT_DB_TYPE_RAM        = "ram"

class CT_DB_INTERFACE(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def connect(self)->[bool, str]:
		pass

	#https://docs.python.org/3/library/sqlite3.html#controlling-transactions
	#'autocommit' is not enable into dafault sqlite3 python instalation module
	@abc.abstractmethod
	def commit(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def rollback(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def createTablesIfNotExist(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def quit(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def createTablesIfNotExist(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def insertCmd(self, cmd : BinanceCTProto.CT_PROTO)->[bool, str]:
		pass

class CT_DB_SQLITE(CT_DB_INTERFACE):
	fileName = ""
	conn = None

	def __init__(self, sqliteFile = ""):
		self.fileName = sqliteFile
		self.conn = None

	def connect(self)->[bool, str]:
		try:
			self.conn = sqlite3.connect(self.fileName)
		except sqlite3.Error as e:
			return([False, e])

		return([True, "Ok"])

	def commit(self)->[bool, str]:
		try:
			self.conn.commit()
		except sqlite3.Error as e:
			return([False, e])

		return([True, "Ok"])

	def rollback(self)->[bool, str]:
		pass

	def quit(self)->[bool, str]:
		try:
			self.conn.close()
		except sqlite3.Error as e:
			return([False, e])

		return([True, "Ok"])

	def createTablesIfNotExist(self)->[bool, str]:
		srvOrdIdcliOrdId_table = "CREATE TABLE IF NOT EXISTS SRVORDIDCLISRVID (" \
		                         "SrvOrdId TEXT NOT NULL, "                      \
		                         "CliOrdId TEXT, "                               \
		                         "PRIMARY KEY('SrvOrdId'));"
		cmd_table = "CREATE TABLE IF NOT EXISTS CMDS (" \
		            "cmd TEXT NOT NULL, "               \
		            "fromid TEXT NOT NULL, "            \
		            "toid TEXT NOT NULL, "              \
		            "timestamp TEXT NOT NULL, "         \
		            "typecmd TEXT NOT NULL, "           \
		            "resp_timestamp TEXT, "             \
		            "datacmd TEXT);"

		createTables = [srvOrdIdcliOrdId_table, cmd_table]

		try:
			[self.conn.execute(i) for i in createTables]
			self.conn.commit()

		except sqlite3.Error as e:
			return([False, f"DB erro createTables Error: {e}"])
		except sqlite3.Warning as e:
			return([False, f"DB erro createTables Warning: {e}"])
		except sqlite3.DatabaseError as e:
			return([False, f"DB erro createTables DatabaseError: {e}"])
		except sqlite3.IntegrityError as e:
			return([False, f"DB erro createTables IntegrityError: {e}"])
		except sqlite3.ProgrammingError as e:
			return([False, f"DB erro createTables ProgrammingError: {e}"])
		except sqlite3.OperationalError as e:
			return([False, f"DB erro createTables OperationalError: {e}"])
		except sqlite3.NotSupportedError as e:
			return([False, f"DB erro createTables NotSupported: {e}"])

		return([True, "Ok"])

	def insertCmd(self, cmd : BinanceCTProto.CT_PROTO = None)->[bool, str]:

		cmdValues = (cmd.cmd, cmd.fromto['from'], cmd.fromto['to'], cmd.timestamp, cmd.cmdtype, cmd.resp_timestamp, f"{cmd.data}")

		cmdInsert = "INSERT INTO CMDS (cmd, fromid, toid, timestamp, typecmd, resp_timestamp, datacmd) VALUES (?, ?, ?, ?, ?, ?, ?)"

		try:
			cur = self.conn.cursor()
			cur.execute(cmdInsert, cmdValues)

			self.conn.commit()

		except sqlite3.Error as e:
			return([False, f"DB erro insertCmd Error: {e}"])
		except sqlite3.Warning as e:
			return([False, f"DB erro insertCmd Warning: {e}"])
		except sqlite3.DatabaseError as e:
			return([False, f"DB erro insertCmd DatabaseError: {e}"])
		except sqlite3.IntegrityError as e:
			return([False, f"DB erro insertCmd IntegrityError: {e}"])
		except sqlite3.ProgrammingError as e:
			return([False, f"DB erro insertCmd ProgrammingError: {e}"])
		except sqlite3.OperationalError as e:
			return([False, f"DB erro insertCmd OperationalError: {e}"])
		except sqlite3.NotSupportedError as e:
			return([False, f"DB erro insertCmd NotSupported: {e}"])

		return([True, "Ok"])

class CT_DB_POSTGRESQL(CT_DB_INTERFACE):
	user   = ""
	passwd = ""
	schema = ""

	def __init__(self, dbuser = "", dbpass = "", dbschema = ""):
		self.user   = dbuser
		self.passwd = dbpass
		self.schema = dbschema

	def connect(self)->[bool, str]:
		return([False, "Not implemented"])

	def commit(self)->[bool, str]:
		return([False, "Not implemented"])

	def rollback(self)->[bool, str]:
		pass

	def createTablesIfNotExist(self)->[bool, str]:
		return([False, "Not implemented"])

	def quit(self)->[bool, str]:
		return([False, "Not implemented"])

	def insertCmd(self, cmd : BinanceCTProto.CT_PROTO)->[bool, str]:
		return([False, "Not implemented"])

class CT_DB_RAM(CT_DB_INTERFACE):
	def connect(self)->[bool, str]:
		return([False, "Not implemented"])

	def commit(self)->[bool, str]:
		return([False, "Not implemented"])

	def rollback(self)->[bool, str]:
		pass

	def quit(self)->[bool, str]:
		return([False, "Not implemented"])

	def createTablesIfNotExist(self)->[bool, str]:
		return([False, "Not implemented"])

	def insertCmd(self, cmd : BinanceCTProto.CT_PROTO)->[bool, str]:
		return([False, "Not implemented"])

class CT_DB:
	engine = ""
	DB = None

	def __init__(self, _engine = "", _sqliteDBFile = "", _dbuser = "", _dbpass = "", _dbschema = ""):
		self.DB = object()
		self.engine = _engine

		if _engine == CT_DB_TYPE_SQLITE:
			self.DB = CT_DB_SQLITE(sqliteFile = _sqliteDBFile)

		elif _engine == CT_DB_TYPE_POSTGRESQL:
			self.DB = CT_DB_POSTGRESQL(dbuser = _dbuser, dbpass = _dbpass, dbschema = _dbschema)

		elif _engine == CT_DB_TYPE_RAM :
			self.DB = CT_DB_RAM()

		else:
			self.DB = None

'''
aaa = CT_DB(_engine = CT_DB_TYPE_SQLITE, _sqliteDBFile = "test.sqlite")
ret,msg = aaa.DB.connect()
aaa.DB.createTablesIfNotExist()
aaa.DB.commit()
aaa.DB.quit()
'''
