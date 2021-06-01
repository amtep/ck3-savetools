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

class ScanElementType(Enum):
    OpenScope = auto()
    CloseScope = auto()
    Assign = auto()
    Value = auto()

OpenScope = namedtuple('OpenScope', ('etype', 'scope', 'key'))
CloseScope = namedtuple('CloseScope', ('etype', 'scope'))
Assign = namedtuple('Assign', ('etype', 'scope', 'key', 'value'))
Value = namedtuple('Value', ('etype', 'scope', 'value'))

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
        for m in tokenRE.finditer(line):
            # The logic here relies on there being only one matching group
            if m.lastgroup == 'WS':
                continue
            if m.lastgroup == 'QuotedString':
                # strip the quotes
                value = line[m.start()+1:m.end()-1]
            else:
                value = line[m.start():m.end()]
            ttype = TokenType[m.lastgroup]
            yield Token(ttype, value, lineno)

class FormatError(Exception):
    def __init__(self, msg, name=None, line=None):
        self.msg = msg
        self.name = name
        self.line = line

    def __str__(self):
        s = ''
        if self.name:
            s += self.name + ':'
        if self.line is not None:
            s += str(self.line) + ':'
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
        self.scanner = self

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
        self.clear()
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
                    raise FormatError("Not a savefile", name=self.pathname)
                self.__load_from(infile)

    def __unexpected_token(self, token):
        return FormatError('unexpected %s token' % token.ttype.name,
                           name=self.name, line=token.line)

    def __load_from(self, f):
        if hasattr(self.scanner, 'set_name'):
            self.scanner.set_name(self.name)
        scopestack = []
        tokens = []
        for token in tokenize(f):
            if token.ttype == TokenType.Error:
                raise FormatError('unexpected character "%s"' % token.value,
                                  name=self.name, line=token.line)

            if len(tokens) == 1:
                if token.ttype == TokenType.Eq:
                    tokens.append(token)
                    continue
                else:
                    # process previous token
                    elem = Value(ScanElementType.Value, tuple(scopestack), tokens[0])
                    tokens = []
                    self.scanner.scan_element(elem)
            # deliberate fallthrough after previous token is processed

            if len(tokens) == 0:
                if token.ttype in (TokenType.Date, TokenType.Number, TokenType.BareString):
                    tokens.append(token)
                    continue
                elif token.ttype == TokenType.QuotedString:
                    elem = Value(ScanElementType.Value, tuple(scopestack), token)
                elif token.ttype == TokenType.Close:
                    if not scopestack:
                        raise FormatError('unmatched }',
                                          name=self.name, line=token.line)
                    elem = CloseScope(ScanElementType.CloseScope, tuple(scopestack))
                    scopestack.pop()
                elif token.ttype == TokenType.Open:
                    # Start of anonymous scope
                    elem = OpenScope(ScanElementType.OpenScope, tuple(scopestack), None)
                    scopestack.append('')
                else:
                    raise self.__unexpected_token(token)
            elif len(tokens) == 2:
                if token.ttype == TokenType.Open:
                    elem = OpenScope(ScanElementType.OpenScope, tuple(scopestack), token)
                    scopestack.append(tokens[0].value)
                elif token.ttype in (TokenType.Date, TokenType.Number, TokenType.BareString, TokenType.QuotedString):
                    elem = Assign(ScanElementType.Assign, tuple(scopestack), tokens[0], token)
                else:
                    raise self.__unexpected_token(token)
                tokens = []
            else:
                tokens = []
                raise self.__unexpected_token(token)
            self.scanner.scan_element(elem)

    def scan_element(self, elem):
        pass
