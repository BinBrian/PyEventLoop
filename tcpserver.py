from acceptor import Acceptor
from tcpconn import TcpConnection
from logger import Logger

NetLog = Logger("net")


class TcpServer:
    def __init__(self, loop, listenAddr, serverName="Default"):
        self.loop = loop
        self.acceptor = Acceptor(self, listenAddr)
        self.acceptor.SetNewConnCallback(self.OnNewConn)
        self.serverName = serverName
        self.nextConnID = 0
        self.conns = {}
        self.onConnectedCallBack = None
        self.onMessageCallBack = None
        self.onDisConnectedCallBack = None

    def Start(self):
        self.acceptor.Listen()

    def GetConnID(self):
        self.nextConnID += 1
        return self.nextConnID

    def Name(self):
        return self.serverName

    def SetOnConnCallback(self, cb):
        self.onConnectedCallBack = cb

    def SetOnMessageCallBack(self, cb):
        self.onMessageCallBack = cb

    def SetOnDisConnectedCallBack(self, cb):
        self.onDisConnectedCallBack = cb

    def OnNewConn(self, socket):
        connID = self.GetConnID()
        NetLog.Info(f"TcpServer.OnNewConn serv:{self.serverName} connid:{connID} fd:{socket.fileno()} addr:{socket}")
        tcpConn = TcpConnection(self, connID, socket, self.RemoveConn, self.onMessageCallBack)
        self.conns[connID] = tcpConn
        tcpConn.Start()
        if self.onConnectedCallBack:
            self.onConnectedCallBack(tcpConn)

    def RemoveConn(self, connID):
        tcpConn = self.conns.pop(connID, None)
        if tcpConn is None:
            NetLog.Warn(f"TcpServer.RemoveConn serv:{self.serverName} connid:{connID} not found")
            return
        NetLog.Info(f"TcpServer.RemoveConn serv:{self.serverName} connid:{connID} fd:{tcpConn.fileno()}")
        if self.onDisConnectedCallBack:
            self.onDisConnectedCallBack(tcpConn)

    def Loop(self, timeout=None):
        self.loop.Loop(timeout)
