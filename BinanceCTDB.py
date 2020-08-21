#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

# i hate python for force me to import this module for a descent class interface, from all of my heart.
import abc

import sqlite3
#import psycopg2

CT_DB_TYPE_SQLITE     = "sqlite"
CT_DB_TYPE_POSTGRESQL = "postgresql"
CT_DB_TYPE_RAM        = "ram"

class CT_DB_INTERFACE(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def connect(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def commit(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def createTablesIfNotExist(self)->[bool, str]:
		pass

	@abc.abstractmethod
	def quit(self)->[bool, str]:
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
		except Error as e:
			return([False, e])

		self.conn.commit()
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

	def createTablesIfNotExist(self)->[bool, str]:
		return([False, "Not implemented"])

	def quit(self)->[bool, str]:
		return([False, "Not implemented"])

class CT_DB_RAM(CT_DB_INTERFACE):
	def connect(self)->[bool, str]:
		return([False, "Not implemented"])

	def commit(self)->[bool, str]:
		return([False, "Not implemented"])

	def quit(self)->[bool, str]:
		return([False, "Not implemented"])

	def createTablesIfNotExist(self)->[bool, str]:
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

aaa = CT_DB(_engine = CT_DB_TYPE_SQLITE, _sqliteDBFile = "test.sqlite")
ret,msg = aaa.DB.connect()
aaa.DB.createTablesIfNotExist()
aaa.DB.commit()
aaa.DB.quit()
