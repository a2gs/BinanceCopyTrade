#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

# i hate python for force me to import this module for a descent class interface, from all of my heart.
import abc

CT_DB_TYPE_SQLITE     = "sqlite"
CT_DB_TYPE_POSTGRESQL = "postgresql"
CT_DB_TYPE_RAM        = "ram"

class CT_INTERFACE(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def connect(self):
		pass

	@abc.abstractmethod
	def commit(self):
		pass

	@abc.abstractmethod
	def quit(self):
		pass


class CT_DB_SQLITE(CT_INTERFACE):
	fileName = ""

	def __init__(self, sqliteFile = ""):
		self.fileName = sqliteFile

	def connect(self):
		print("connect sqlite")

	def commit(self):
		print("commit sqlite")

	def quit(self):
		print("quit sqlite")

class CT_DB_POSTGRESQL(CT_INTERFACE):
	user   = ""
	passwd = ""
	schema = ""

	def __init__(self, dbuser = "", dbpass = "", dbschema = ""):
		self.user   = dbuser
		self.passwd = dbpass
		self.schema = dbschema

	def connect(self):
		pass

	def commit(self):
		pass

	def quit(self):
		pass

class CT_DB_RAM(CT_INTERFACE):
	def connect(self):
		pass

	def commit(self):
		pass

	def quit(self):
		pass

	def f1(self):
		print(">>>>f1")

class CT_DB:
	engine = ""
	DB = 0

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

aaa = CT_DB(_engine = "sqlite", _sqliteDBFile = "test")
bbb = CT_DB(_engine = "postgresql")
ccc = CT_DB(_engine = "ram")

aaa.DB.connect()
bbb.DB.quit()
ccc.DB.f1()
