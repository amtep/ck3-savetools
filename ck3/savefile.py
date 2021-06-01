import io
import os
import re

from collections import namedtuple
from enum import Enum, auto
from zipfile import ZipFile, BadZipFile

# TODO add paths for other systems
CK3_SAVEFILE_DIRS = [
    '~/.local/share/Paradox Interactive/Crusader Kings III/save games/',
]

class TokenType(Enum):
    Error = auto()
    BareString = auto()
    Eq = auto()
    Open = auto()
    Close = auto()
    Number = auto()
    Date = auto()
    QuotedString = auto()

Token = namedtuple('Token', ('ttype', 'value', 'line'))

tokenRE = re.compile(r"""
(?P<WS>\s+) |
(?P<Eq>=) |
(?P<Open>{) |
(?P<Close>}) |
(?P<Date>\d+[.] \d+[.] \d+) |
(?P<Number>-?\d+[.]?\d* | -?[.]\d+) |
(?P<BareString>[\w.:_] [\d\w.:_-]*) |
(?P<QuotedString>"[^"]*") |
(?P<Error>.)
""", re.VERBOSE | re.ASCII)

def tokenize(f):
    lineno = 0
    for line in f:
        lineno += 1
        pos = 0
        while pos < len(line):
            m = tokenRE.match(line, pos)
            pos = m.end()
            if m.group('WS'):
                continue
            if m.group('QuotedString'):
                # strip the quotes
                value = line[m.start()+1:m.end('QuotedString')-1]
            else:
                value = line[m.start():m.end()]
            ttype = TokenType[m.lastgroup]
            yield Token(ttype, value, lineno)

class FormatError(Exception):
    def __init__(self, msg, savename=None):
        self.msg = msg
        self.savename = savename

    def __str__(self):
        s = ''
        if self.savename:
            s += self.savename + ':'
        if s:
            s += ' '
        s += self.msg
        return s

class SaveFile:
    def __init__(self):
        self.clear()

    def clear(self):
        self.name = None
        self.pathname = None

    def load(self, name):
        if os.path.dirname(name):
            # exact path
            self.load_pathname(name)
            return

        if not name.endswith(".ck3"):
            name += ".ck3"
        for path in CK3_SAVEFILE_DIRS:
            path = os.path.expanduser(path)
            pathname = os.path.join(path, name)
            if os.path.isfile(pathname):
                self.load_pathname(pathname)
                return
        raise OSError("Savefile not found")

    def load_pathname(self, pathname):
        self.pathname = pathname
        self.name = os.path.splitext(os.path.basename(pathname))[0]
        try:
            z = ZipFile(pathname)
            with z.open('gamestate') as infile:
                self.__load_from(io.TextIOWrapper(infile, encoding='utf-8'))
        except BadZipFile:
            with open(pathname, 'rt', encoding='utf-8') as infile:
                checksum = f.readline()
                if not checksum.startswith("SAV"):
                    raise FormatError("Not a savefile", savename=self.pathname)
                self.__load_from(infile)

    def __load_from(self, f):
        for ttype, value, lineno in tokenize(f):
            if ttype == TokenType.Error:
                print((ttype, value, lineno))
