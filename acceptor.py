from channel import Channel
from logger import Logger

import socket as mod_socket

NetLog = Logger("net")


class Acceptor:
    def __init__(self, serv, addr, backlogs=100):
        self.serv = serv
        self.addr = addr
        self.listening = False

        socket = mod_socket.socket(mod_socket.AF_INET, mod_socket.SOCK_STREAM)
        socket.setblocking(False)
        socket.bind(addr)
        socket.listen(backlogs)
        self.socket = socket
        channel = Channel(serv.loop, socket)
        channel.SetReadCallBack(self.OnReadCallBack)

        self.channel = channel
        self.OnNewConnCallBack = None

    def Listen(self, backlog=100):
        NetLog.Trace(f"Acceptor.Listen fd:{self.socket.fileno()} serv:{self.serv.Name()} backlog:{backlog}")
        self.socket.listen(backlog)
        self.channel.EnableReading()
        self.listening = True

    def SetNewConnCallback(self, cb):
        self.OnNewConnCallBack = cb

    def OnReadCallBack(self):
        listener = self.socket
        connector, addr = listener.accept()
        if self.OnNewConnCallBack:
            self.OnNewConnCallBack(connector)
        else:
            NetLog.Warn(f"Acceptor.OnReadCallBack serv:{self.serv.Name()} not setting callback, close sock:{connector} addr:{addr}")
            connector.close()

    def Destroy(self):
        self.channel.Destroy()
        self.channel = None
        self.socket.close()
        self.serv = None
