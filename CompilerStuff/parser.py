from scanner import *
from tag import Tag


class Env(object):

    def __init__(self, n):
        self.table = {}
        self.prev = n

    def put(self, w, i):
        self.table[w] = i

    def get(self, w):
        e = self
        while e is not None:
            if w in e.table:
                return e.table[w]
            e = e.prev

class Parser(object):

    def __init__(self, scanner):
        self.lex = scanner
        self.look = None
        self.top = None
        self.used = 0
        self.move()

    def move(self):
        try:
            self.look = self.lex.scan()
        except IOError as err:
            raise err

    def error(self, s):
        raise Exception('near line ' + str(self.lex.prog_counter) + ': '
                         + s)

    def match(self, t):
        if self.look.tag == t:
            self.move()
        else:
            self.error('syntax error')

    def program(self):
        s = self.block()
        begin = s.newlabel()
        after = s.newlabel()
        s.emitlabel(begin)
        s.gen(begin, after)
        s.emitlabel(after)

    def block(self):
        self.match('{')
        savedEnv = self.top
        self.top = Env(self.top)
        self.decls()
        s = self.stmts()
        self.match('}')
        self.top = savedEnv
        return s

    def decls(self):
        while self.look.tag is Tag.BASIC:
            p = self.type()
            tok = self.look
            self.match(Tag.ID)
            self.match(';')
            if self.top:
                self.top.put(tok, Id(tok, p, self.used))
            self.used = self.used + p.width

    def type(self):
        p = self.look
        self.match(Tag.BASIC)
        if self.look.tag is not '[':
            return p
        else:
            return self.dims(p)

    def dims(self):
        self.match('[')
        tok = self.look
        self.match(Tag.NUM)
        self.match(']')
        if self.look.tag is '[':
            p = dims(p)
            return Array(tok.value, p)

    def stmt(self):
        tag = self.look.tag
        if tag is ';':
            self.move()
            return Stmt.Null
        elif tag is Tag.IF:
            self.match(Tag.IF)
            self.match('(')
            x = self.bool()
            self.match(')')
            self.s1 = self.stmt()
            if tag is not Tag.ELSE:
                return If(x, self.s1)
            self.match(Tag.ELSE)
            s2 = self.stmt()
            return Else(x, self.s1, self.s2)
        elif tag is Tag.WHILE:
            whilenode = While()
            savedStmt = Stmt.Enclosing
            Stmt.Enclosing = whilenode
            self.match(Tag.WHILE)
            self.match('(')
            x = self.bool()
            self.match(')')
            self.s1 = self.stmt()
            whilenode.init(x, self.s1)
            Stmt.Enclosing = savedStmt
            return whilenode
        elif tag is Tag.DO:
            donode = Do()
            savedStmt = Stmt.Enclosing
            Stmt.Enclosing = donode
            self.match(Tag.DO)
            self.s1 = self.stmt()
            self.match(Tag.WHILE)
            self.match('(')
            x = self.bool()
            self.match(')')
            self.match(';')
            donode.init(self.s1, x)
            Stmt.Enclosing = savedStmt
            return donode
        elif tag is Tag.BREAK:
            self.match(Tag.BREAK)
            self.match(';')
            return Break()
        elif tag is '{':
            return self.block()
        else:
            return self.assign()

    def stmts(self):
        if self.look.tag is '}':
            return Stmt.Null
        else:
            return Seq(self.stmt(), self.stmts())

    def assign(self):
        stmt = None
        t = self.look
        self.match(Tag.ID)
        t_id = self.top.get(t)
        if t_id is None:
            self.error(t.__repr__() + ' undeclared')
        if self.look.tag is '=':    # S -> id = E ; -> requires space before ';'
            self.move()
            stmt = Set(t_id, self.bool())
        else:
            x = self.offset(t_id)
            self.match('=')
            stmt = SetElem(x, self.bool())
        print(stmt.id, stmt.expr)
        self.match(';')
        return stmt

    def bool(self):
        x = self.join()
        while self.look.tag == Tag.OR:
            tok = self.look
            self.move()
            x = Or(tok, x, self.join())
        return x

    def join(self):
        x = self.equality()
        while self.look.tag == Tag.AND:
            tok = self.look
            self.move()
            x = And(tok, x, self.equality())
        return x

    def equality(self):
        x = self.rel()
        while self.look.tag == Tag.EQ or self.look.tag == Tag.NE:
            tok = self.look
            self.move()
            x = Rel(tok, x, self.rel())
        return x

    def rel(self):
        x = self.expr()
        tag = self.look.tag
        if tag is '<' or tag is Tag.LE or tag is Tag.GE or tag is '>':
            tok = self.look
            self.move()
            return Rel(tok, x, self.expr())
        return x

    def expr(self):
        x = self.term()
        while self.look.tag is '+' or self.look.tag is '-':
            tok = self.look
            self.move()
            x = Arith(tok, x, self.term())
        return x

    def term(self):
        x = self.unary()
        while self.look.tag is '*' or self.look.tag is '/':
            tok = self.look
            self.move()
            x = Arith(tok, x, self.unary())
        return x

    def unary(self):
        if self.look.tag == '-':
            self.move()
            return Unary(Word.minus, self.unary())
        elif self.look.tag == '!':
            tok = self.look
            self.move()
            return Not(tok, self.unary())
        else:
            return self.factor()

    def factor(self):
        x = None
        tag = self.look.tag
        print(tag, 'factor')
        if tag is '(':
            self.move()
            x = self.bool()
            self.match(')')
        elif tag is Tag.NUM:
            x = Constant(self.look, Type.Int)
            self.move()
            return x
        elif tag is Tag.REAL:
            x = Constant(self.look, Type.Float)
            self.move()
            return x
        elif tag is Tag.TRUE:
            x = Constant.true
            self.move()
            return x
        elif tag is Tag.FALSE:
            x = Constant.false
            self.move()
            return x
        elif tag is Tag.ID:
            t_id = self.top.get(self.look)
            if not t_id:
                self.error(self.look.__repr__() + ' undeclared')
            self.move()
            if self.look.tag != '[':
                return t_id
            else:
                return self.offset(t_id)
        else:
            self.error('syntax error')
            return x

    def offset(self, a):
        t_type = a.t_type
        self.match('[')
        i = self.bool()
        self.match(']')
        t_type = t_type.of
        w = Constant(t_type.width)
        t1 = Arith(Token('*'), i, w)
        loc = t1
        while self.look.tag is '[':
            self.match('[')
            i = self.bool()
            self.match(']')
            t_type = t_type.of
            w = Constant(t_type.width)
            t1 = Arith(Token('*'), i, w)
            t2 = Arith(Token('+'), loc, t1)
            loc = t2
        return Access(a, loc, t_type)
