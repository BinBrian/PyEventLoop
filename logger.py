import sys


# FIXME: 支持同时打印到控制台+文件
# FIXME: 若异常抛出导致程序挂掉，也要输出到文件
class Logger:
    level = 2

    def __init__(self, moduleName):
        self.moduleName = moduleName

    def Trace(self, text):
        if self.level > 0:
            return
        print(f"[TRACE][{self.moduleName}]{text}", file=sys.stdout, flush=True)

    def Debug(self, text):
        if self.level > 1:
            return
        print(f"[DEBUG][{self.moduleName}]{text}", file=sys.stdout, flush=True)

    def Info(self, text):
        print(f"[INFO][{self.moduleName}]{text}", file=sys.stdout, flush=True)

    def Warn(self, text):
        print(f"[WARN][{self.moduleName}]{text}", file=sys.stdout, flush=True)

    def Error(self, text):
        print(f"[ERROR][{self.moduleName}]{text}", file=sys.stderr, flush=True)
