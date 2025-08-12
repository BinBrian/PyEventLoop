from defines import kNew
from logger import Logger

import selectors

NetLog = Logger("net")


class Channel:
    def __init__(self, loop, socket):
        self.fd = socket.fileno()
        self._loop = loop
        self.socket = socket
        self.readCallBack = None
        self.writeCallBack = None
        self._events = 0
        self._attached = False
        self._index = kNew  # used by eventloop

    def Events(self):
        return self._events

    def SetReadCallBack(self, cb):
        self.readCallBack = cb

    def SetWriteCallBack(self, cb):
        self.writeCallBack = cb

    def SetIndex(self, index):
        self._index = index

    def Index(self):
        return self._index

    def IsNoneEvent(self):
        return self._events == 0

    def EnableReading(self):
        self._attached = True
        self._events |= selectors.EVENT_READ
        self._UpdateToLoop()

    def EnableWriting(self):
        if self._events & selectors.EVENT_WRITE:
            return
        self._attached = True
        self._events |= selectors.EVENT_WRITE
        self._UpdateToLoop()

    def DisableWriting(self):
        if not (self._events & selectors.EVENT_WRITE):
            return
        assert self._attached
        self._events ^= selectors.EVENT_WRITE
        self._UpdateToLoop()

    def DisableAll(self):
        assert self._attached
        self._events = 0
        self._UpdateToLoop()

    def _UpdateToLoop(self):
        self._loop.UpdateChannel(self)

    def HandleEvents(self, mask):
        if not self._attached:  # 可能取消注册时，已经在就绪列表中，这次通知要拦截
            return
        NetLog.Trace(f"Channel.HandleEvents fd:{self.fd} mask:{mask}")
        if mask & selectors.EVENT_READ and self.readCallBack:
            self.readCallBack()
        if mask & selectors.EVENT_WRITE and self.writeCallBack:
            self.writeCallBack()

    def Disattach(self):
        if not self._attached:
            return
        NetLog.Trace(f"Channel.Disattach fd:{self.fd}")
        self._loop.RemoveChannel(self)
        self._attached = False

    def Destroy(self):
        NetLog.Trace(f"Channel.Destroy fd:{self.fd}")
        self.Disattach()
        self._loop = None
        self.socket = None
        self.readCallBack = None
        self.writeCallBack = None
