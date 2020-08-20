#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

import socket
import struct

class connection:

	servsock = 0
	clientsock = 0 # TODO: a list/vector to accept multi clients

	def __init__(self):
		self.servsock = 0
		self.clientsock = 0

	def serverLoad(self, family, socktype):
		self.servsock = socket.socket(family, socktype)

	def serverBindListen(self, port : int, listen : int):
		self.servsock.bind((socket.gethostname(), port))
		self.servsock.listen(listen)

	def sockOpts(self, opt):
		self.servsock.setsockopt(socket.SOL_SOCKET, opt, 1)

	def endServer(self):
		self.servsock.shutdown(socket.SHUT_RDWR)

	def endClient(self):
		self.clientsock.shutdown(socket.SHUT_RDWR)

	def serverAccept(self):
		self.clientsock, address = self.servsock.accept()
		return address

	def connectToServer(self, address, port, family, socktype)->[bool, str]:
		self.clientsock = socket.socket(family, socktype)

		try:
			self.clientsock.connect((address, port))
		except ConnectionRefusedError as e:
			return([False, e])

		return([True, "Ok"])

	def sendMsg(self, msg, szToSend):
		msgSz = struct.pack('!I', szToSend)

		try:
			self.clientsock.sendall(msgSz)
			self.clientsock.sendall(bytes(msg, "utf-8"))
		except:
			raise

	def recvMsg(self) -> str:
		HEADERSIZE = 4 # struct.pack('!I', szToSend)

		msgSz   = 0
		recvBuf = b''
		chunk   = b''

		# reading msg size
		recvBufSz = 0

		while recvBufSz < HEADERSIZE:

			chunk = self.clientsock.recv(HEADERSIZE - recvBufSz)

			if chunk == b'':
				raise RuntimeError("socket connection broken")

			recvBuf = recvBuf + chunk
			recvBufSz = len(recvBuf)

		msgSz = struct.unpack('!I', recvBuf)[0]

		# reading the msg
		recvBuf   = b''
		recvBufSz = 0

		while recvBufSz < msgSz:

			chunk = self.clientsock.recv(msgSz - recvBufSz)

			if chunk == b'':
				raise RuntimeError("socket connection broken")

			recvBuf = recvBuf + chunk
			recvBufSz = len(recvBuf)

		return recvBuf.decode("utf-8")
