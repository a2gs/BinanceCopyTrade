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

	def serverLoad(self, family, socktype)->[bool, str]:
		try:
			self.servsock = socket.socket(family, socktype)
		except OSError as e:
			return([False, f"{e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"BaseException {str(e)}"])
		except:
			return([False, "Unknow exception"])

		return([True, "Ok"])

	def serverBindListen(self, port : int, listen : int)->[bool, str]:
		try:
			self.servsock.bind((socket.gethostname(), port))
			self.servsock.listen(listen)
		except OSError as e:
			return([False, f"{e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"BaseException {str(e)}"])
		except:
			return([False, "Unknow exception"])

		return([True, "Ok"])

	def sockOpts(self, opt)->[bool, str]:
		try:
			self.servsock.setsockopt(socket.SOL_SOCKET, opt, 1)
		except OSError as e:
			return([False, f"{e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"BaseException {str(e)}"])
		except:
			return([False, "Unknow exception"])

		return([True, "Ok"])

	def endServer(self)->[bool, str]:
		try:
			self.servsock.shutdown(socket.SHUT_RDWR)
		except OSError as e:
			return([False, f"{e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"BaseException {str(e)}"])
		except:
			return([False, "Unknow exception"])

		return([True, "Ok"])

	def endClient(self)->[bool, str]:
		try:
			self.clientsock.shutdown(socket.SHUT_RDWR)
		except OSError as e:
			return([False, f"{e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"BaseException {str(e)}"])
		except:
			return([False, "Unknow exception"])

		return([True, "Ok"])

	def serverAccept(self)->[bool, str, str]:
		try:
			self.clientsock, address = self.servsock.accept()
		except OSError as e:
			return([False, f"{e.errno} {e.strerror}", ""])
		except ConnectionError as e:
			return([False, f"ConnectionError {e}", ""])
		except KeyboardInterrupt:
			return([False, "KeyboardInterrupt", ""])
		except Exception as e:
			return([False, e, ""])
		except BaseException as e:
			return([False, f"BaseException {str(e)}", ""])
		except:
			return([False, "Unknow exception", ""])

		return([True, "Ok", address])

	def connectToServer(self, address, port, family, socktype)->[bool, str]:
		try:
			self.clientsock = socket.socket(family, socktype)
		except OSError as e:
			return([False, f"Erro socket: {e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"Erro socket: ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "Erro socket: KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"Erro socket: BaseException {str(e)}"])
		except:
			return([False, "Erro socket: unknow exception"])

		# i hate 'exception' (in c++ too, the ideia). i intentionally do bad code on purpose with it.
		try:
			self.clientsock.connect((address, port))
		except OSError as e:
			return([False, f"Erro connect: {e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"Erro connect: ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "Erro connect: KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"Erro connect: BaseException {str(e)}"])
		except:
			return([False, "Erro connect: unknow exception"])

		return([True, "Ok"])

	def sendMsg(self, msg, szToSend)->[bool, str]:
		msgSz = struct.pack('!I', szToSend)

		try:
			self.clientsock.sendall(msgSz)
			self.clientsock.sendall(bytes(msg, "utf-8"))
		except OSError as e:
			return([False, f"{e.errno} {e.strerror}"])
		except ConnectionError as e:
			return([False, f"ConnectionError {e}"])
		except KeyboardInterrupt:
			return([False, "KeyboardInterrupt"])
		except Exception as e:
			return([False, e])
		except BaseException as e:
			return([False, f"BaseException {str(e)}"])
		except:
			return([False, "Unknow exception"])

		return([True, "Ok"])

	def recvMsg(self)->[bool, str, str]:
		HEADERSIZE = 4 # struct.pack('!I', szToSend)

		msgSz   = 0
		recvBuf = b''
		chunk   = b''

		# reading msg size
		recvBufSz = 0

		while recvBufSz < HEADERSIZE:

			try:
				chunk = self.clientsock.recv(HEADERSIZE - recvBufSz)
			except OSError as e:
				return([False, f"Erro reading msg envelop: {e.errno} {e.strerror}", ""])
			except ConnectionError as e:
				return([False, f"Erro reading msg envelop: ConnectionError {e}", ""])
			except KeyboardInterrupt:
				return([False, "Erro reading msg envelop: KeyboardInterrupt", ""])
			except Exception as e:
				return([False, f"Erro reading msg envelop: {e}", ""])
			except BaseException as e:
				return([False, f"Erro reading msg envelop: BaseException {str(e)}", ""])
			except:
				return([False, "Erro reading msg envelop: Unknow exception", ""])

			if chunk == b'':
				return([False, "Socket connection broken", ""])

			recvBuf = recvBuf + chunk
			recvBufSz = len(recvBuf)

		msgSz = struct.unpack('!I', recvBuf)[0]

		# reading the msg
		recvBuf   = b''
		recvBufSz = 0

		while recvBufSz < msgSz:

			try:
				chunk = self.clientsock.recv(msgSz - recvBufSz)
			except OSError as e:
				return([False, f"Erro reading msg: {e.errno} {e.strerror}", ""])
			except ConnectionError as e:
				return([False, f"Erro reading msg: ConnectionError {e}", ""])
			except KeyboardInterrupt:
				return([False, "Erro reading msg: KeyboardInterrupt", ""])
			except Exception as e:
				return([False, f"Erro reading msg: {e}", ""])
			except BaseException as e:
				return([False, f"Erro reading msg: BaseException {str(e)}", ""])
			except:
				return([False, "Erro reading msg: Unknow exception", ""])

			if chunk == b'':
				return([False, "Socket connection broken", ""])

			recvBuf = recvBuf + chunk
			recvBufSz = len(recvBuf)

		return([True, "Ok", recvBuf.decode("utf-8")])
