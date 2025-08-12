from logger import Logger
from defines import *

import selectors

NetLog = Logger("net")


class EventLoop:

    def __init__(self, selector: selectors.DefaultSelector):
        self.selector = selector
        self.channels = {}

    def UpdateChannel(self, channel):
        index = channel.Index()
        evs = channel.Events()

        NetLog.Trace(f"EventLoop.UpdateChannel fd:{channel.fd} evs:{evs} index:{index}")

        if channel.fd not in self.channels:
            self.channels[channel.fd] = channel

        if index == kNew or index == kDel:
            if evs == 0:
                return
            else:
                NetLog.Trace(f"EventLoop.UpdateChannel fd:{channel.fd} evs:{evs} add")
                self.selector.register(channel.socket, evs, channel.HandleEvents)
                channel.SetIndex(kAdd)
        else:
            if evs == 0:
                NetLog.Trace(f"EventLoop.UpdateChannel fd:{channel.fd} evs:{evs} del")
                self.selector.unregister(channel.socket)
                channel.SetIndex(kDel)
            else:
                self.selector.modify(channel.socket, evs, channel.HandleEvents)

    def RemoveChannel(self, channel):
        fd = channel.fd
        chan = self.channels.pop(fd, None)
        if not chan:
            NetLog.Warn(f"EventLoop.RemoveChannel fd:{fd} not found!")
            return
        index = channel.Index()
        if index == kAdd:
            NetLog.Trace(f"EventLoop.RemoveChannel fd:{fd} del")
            self.selector.unregister(channel.socket)
        channel.SetIndex(kDel)

    def Loop(self, timeout=None):  # FIXME: 优雅退出
        while True:
            events = self.selector.select(timeout)
            for key, mask in events:
                NetLog.Trace(f"TcpServer.Loop key:{key} mask:{mask}")
                if mask == 0:
                    NetLog.Warn(f"TcpServer.Loop key:{key} mask:{mask} empty events")
                fn = key.data
                fn(mask)
