from logger import Logger
from eventloop import EventLoop
from tcpserver import TcpServer

import selectors
import sys
import traceback

EchoLog = Logger("echo")


def HookException(t, val, tb):
    traceback.print_exception(t, val, tb)
    # 异常时，顺便把当时的局部变量打印出来。
    while tb:
        tb1 = tb.tb_next
        sys.stderr.flush()
        if not tb1:
            extend = []
            localvars = f"local variables: {tb.tb_frame.f_locals} {extend}\n"
            sys.stderr.write(localvars)
            sys.stderr.flush()
        tb = tb1


import socket as mod_socket


def OnMessage(tcpConn, data):
    EchoLog.Info(f"OnMessage connid:{tcpConn.connID} data:{data}")
    try:
        text = data.decode("utf-8").strip()
        if text == "kick":
            tcpConn.Close()
        elif text == "shutdown":
            tcpConn.Send("bye~".encode("utf-8"))
            tcpConn.ShutDown()
        else:
            tcpConn.Send(data)
    except UnicodeDecodeError:
        pass


def OnConnected(tcpConn):
    EchoLog.Info(f"OnConnected connid:{tcpConn.connID}")


def OnDisConnected(tcpConn):
    EchoLog.Info(f"OnDisConnected connid:{tcpConn.connID}")


# sys.stdout = open("echo.log", "w")
# sys.stderr = open("err.log", "w")

sys.excepthook = HookException
# FIXME: 单独关闭读端和全关闭时，直接select会抛异常
eventloop = EventLoop(selectors.DefaultSelector())
server = TcpServer(eventloop, ('localhost', 1234), serverName="EchoServer")
server.SetOnConnCallback(OnConnected)
server.SetOnMessageCallBack(OnMessage)
server.SetOnDisConnectedCallBack(OnDisConnected)
server.Start()
server.Loop()
