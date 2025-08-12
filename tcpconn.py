from channel import Channel
from logger import Logger

import socket

NetLog = Logger("net")


class TcpConnection:
    def __init__(self, serv, connID, socket, onDisConnectedCallBack, onMessageCallBack=None):
        self.serv = serv
        self.connID = connID

        socket.setblocking(False)
        self.socket = socket

        channel = Channel(serv.loop, socket)
        channel.SetReadCallBack(self.HandleRead)
        channel.SetWriteCallBack(self.HandleWrite)
        self.channel = channel

        self.onMessageCallBack = onMessageCallBack
        self.onDisconnectCallBack = onDisConnectedCallBack

        self.outputs = bytes()

    def Start(self):
        self.channel.EnableReading()

    def HandleRead(self):
        data = self.socket.recv(4096)  # FIXME: input buff
        if data:
            if self.onMessageCallBack:
                self.onMessageCallBack(self, data)
        else:
            self.HandleClose(active=False)

    def HandleClose(self, active: bool):
        NetLog.Info(f"TcpConnection.HandleClose connid:{self.connID} fd:{self.fileno()} active:{active}")
        self.channel.DisableAll()
        assert self.onDisconnectCallBack is not None
        self.onDisconnectCallBack(self.connID)
        self.Destroy()

    def HandleWrite(self):  # FIXME:更高效拼装bytes
        if self.outputs:
            oldLen = len(self.outputs)
            wLen = self.socket.send(self.outputs)
            NetLog.Trace(f"TcpConnection.HandleWrite connid:{self.connID} fd:{self.fileno()} nw:{wLen} nl:{max(oldLen - wLen, 0)}")
            if wLen >= oldLen:
                self.outputs = bytes()
                self.channel.DisableWriting()
            else:
                self.outputs = self.outputs[wLen:]
                self.channel.EnableWriting()
        else:
            self.channel.DisableWriting()

    def fileno(self):
        return self.socket.fileno()

    def Send(self, data: bytes):
        NetLog.Trace(f"TcpConnection.Send connid:{self.connID} fd:{self.fileno()} add:{len(data)} total:{len(self.outputs) + len(data)}")
        self.outputs += data
        self.HandleWrite()  # 直接写入,下一tick再写会丢数据

    def ShutDown(self):
        NetLog.Trace(f"TcpConnection.ShutDown connid:{self.connID} fd:{self.fileno()} nl:{len(self.outputs)}")
        self.socket.shutdown(socket.SHUT_WR)  # 必然只能关闭写端
        self.channel.DisableWriting()

    def Close(self):
        NetLog.Trace(f"TcpConnection.Close connid:{self.connID} fd:{self.fileno()}")
        self.HandleClose(active=True)

    def Destroy(self):
        NetLog.Trace(f"TcpConnection.Destroy connid:{self.connID} fd:{self.fileno()}")
        self.channel.Destroy()
        self.socket.close()
        self.onDisconnectCallBack = None
