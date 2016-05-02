import sys
from tag import Tag

class Scanner(object):
	prog_counter = 1
	error_status = 0
	def __init__(self, filename):
		Scanner.prog_counter = 1
		Scanner.error_status = 0
		self.symbol_table = {}
		if filename is not None:
			self.file = open(filename, 'r')
		else:
			self.file = None

		self.peek = ' '

		self.reserveWord(Word("if", Tag.IF))
		self.reserveWord(Word("else", Tag.ELSE))
		self.reserveWord(Word("while", Tag.WHILE))
		self.reserveWord(Word("do", Tag.DO))
		self.reserveWord(Word("break", Tag.BREAK))
		self.reserveWord(Word.true)
		self.reserveWord(Word.false)
		self.reserveWord(Type.Int)
		self.reserveWord(Type.Char)
		self.reserveWord(Type.Bool)
		self.reserveWord(Type.Float)

	def reportError(self, exception):
		error_status = 'e'
		raise exception

	def reportWarning(self, exception):
		error_status = 'w'

	def readch(self, c=None):
		self.peek = self.file.read(1)
		if self.peek != c:
			return False
		if c is not None:
			self.peek = ' '
			return True

	def isDigit(self, s):
		return str.isdigit(s)

	def isLetter(self, s):
		return str.isalpha(s)

	def getToken(self):
		if self.peek == '&':
			if self.readch('&'):
				return Word.t_and
			else:
				return Token('&')
		elif self.peek == '|':
			if self.readch('|'):
				return Word.t_or
			else:
				return Token('|')
		elif self.peek == '=':
			if self.readch('='):
				return Word.eq
			else:
				return Token('=')
		elif self.peek == '!':
			if self.readch('='):
				return Word.ne
			else:
				return Token('|')
		elif self.peek == '<':
			if self.readch('='):
				return Word.le
			else:
				return Token('<')
		elif self.peek == '>':
			if self.readch('='):
				return Word.ge
			else:
				return Token('>')

	def scan(self):
		# also need to implement comments and nested comments here ..
		while(True):
			self.readch()
			if self.peek == ' ' or self.peek == '\t':
				pass
			elif self.peek == '\n':
				self.prog_counter += 1
			else:
				break
		# print(self.peek, "test)")
		# if self.peek == '/':
		# 	if self.readch('/'):
		# 		print("single line comment")
		# 		while True:
		# 			self.readch()
		# 			if self.peek == '\n':
		# 				self.prog_counter += 1
		# 				break
		# 	elif self.readch('*'):
		# 		print("multiline")
		# 		flag = 1
		# 		while flag > 0:
		# 			print("flag")
		# 			self.readch()
		# 			if self.peek == "*":
		# 				if self.readch('/'):
		# 					flag -= 1
		# 			elif self.peek == "/":
		# 				if self.readch('*'):
		# 					flag += 1
		# 			elif self.peek == '\n':
		# 				self.prog_counter += 1
		# 	print("this is reached", self.peek)

		result = self.getToken()
		if result:
			return result

		if(self.isDigit(self.peek)):
			v = int(self.peek)
			self.readch()
			while self.isDigit(self.peek):
				v = 10*v + int(self.peek)
				self.readch()
			if self.peek is not '.':
				return Num(v)
			x = v
			d = 10.0
			while(True):
				self.readch()
				if( not self.isDigit(self.peek)):
					break
				x = x + int(self.peek)/d
				d = d*10.0
			return Real(x)

		if(self.isLetter(self.peek)):
			b = []
			while(True):
				if self.isLetter(self.peek) or self.isDigit(self.peek):
					b.append(self.peek)
					self.readch()
				else:
					break
			s = ''.join(b)
			if s in self.symbol_table:
				return self.symbol_table[s]
			w = Word(s, Tag.ID)
			self.symbol_table[s] = w
			#print(w, w.tag)
			return w

		tok = Token(self.peek)
		#print(tok, self.peek)
		self.peek = ' '

		return tok

	def reserveWord(self, word):
		self.symbol_table[word.string] = word

class Token(object):
	def __init__(self, tag):
		self.tag = tag

	def __repr__(self):
		return "" + self.tag

class Num(Token):
	def __init__(self, value):
		super(Num, self).__init__(Tag.NUM)
		self.value = value

	def __repr__(self):
		return "" + str(self.value)

class Real(Token):
	def __init__(self, value):
		super(Real, self).__init__(Tag.REAL)
		self.value = value

	def __repr__(self):
		return "" + self.value

class Word(Token):
	def __init__(self, string, tag):
		super(Word, self).__init__(tag)
		self.string = string

	def __repr__(self):
		return self.string

Word.t_and = Word("&&", Tag.AND)
Word.t_or = Word("||", Tag.OR)
Word.eq = Word("==", Tag.EQ)
Word.ne = Word("!=", Tag.NE)
Word.le = Word("<=", Tag.LE)
Word.ge = Word(">=", Tag.GE)
Word.minus = Word("minus", Tag.MINUS)
Word.true = Word("true", Tag.TRUE)
Word.false = Word("false", Tag.FALSE)
Word.temp = Word("t", Tag.TEMP)

class Type(Word):
	def __init__(self, string, tag, width):
		super(Type, self).__init__(string, tag)
		self.width = width

	@staticmethod
	def numeric(p):
		return p == Type.Char or p == Type.Int or p == Type.Float

	@staticmethod
	def max(self, p1, p2):
		if not Type.numeric(p1) or not Type.numeric(p2):
			return None
		elif p1 is Type.Float or p2 is Type.Float:
			return Type.Float
		elif p1 is Type.Int or p2 is Type.Int:
			return Type.Int
		else:
			return Type.Char

Type.Int = Type("int", Tag.BASIC, 4)
Type.Float = Type("float", Tag.BASIC, 8)
Type.Char = Type("char", Tag.BASIC, 1)
Type.Bool = Type("bool", Tag.BASIC, 1)

class Array(Type):
	def __init__(size, p):
		super(Array, self).__init__("[]", Tag.INDEX, size*p.width)
		self.size = size
		self.of = p

	def __repr__(self):
		return "[" + size + "] " + self.of

class Node(object):
	labels = 0

	def __init__(self, line=0):
		self.line = Scanner.prog_counter

	def error(self, string):
		raise Exception("near line " + self.line + ": " + string)

	def newlabel(self):
		Node.labels += 1
		return Node.labels

	def emitlabel(self, i):
		print("L" + i + ":")

	def emit(self, s):
		print("\t" + s)

class Expr(Node):
	def __init__(self, token, p):
		self.op = token
		self.type = p

	def gen(self):
		return self

	def reduce(self):
		return self

	def jumping(self, t, f):
		emitjumps(self.__repr__(), t, f)

	def emitjumps(self, test, t, f):
		if t != 0 and f != 0:
			self.emit("if " + test + " goto L" + t)
			self.emit("goto L" + f)
		elif t != 0:
			self.emit("if " + test + " goto L" + t)
		elif f != 0:
			self.emit("iffalse " + test + " goto L" + f)

	def __repr__(self):
		return self.op.__repr__()

class Id(Expr):
	def __init__(self, t_id, p, b):
		super(Id, self).__init__(t_id, p)
		self.offset = b

class Op(Expr):
	def __init__(self, token, p):
		super(Op, self).__init__(token, p)

	def reduce(self):
		x = gen()
		t = Temp(self.type)
		emit(t + " = " + x)
		return t

class Arith(Op):
	def __init__(self, token, x1, x2):
		super(Arith, self).__init__(token, None)
		self.expr1 = x1
		self.expr2 = x2
		t_type = Type.max(expr1.type, expr2.type)
		if not t_type:
			error("type error")

	def gen(self):
		return Arith(self.op, self.expr1.reduce(), self.expr2.reduce())

	def __repr__():
		return self.expr1 + " " + self.op + " " + self.expr2

class Temp(Expr):
	count = 0

	def __init__(self, p):
		super(Temp, self).__init__(Word.temp, p)
		Temp.count += 1
		self.number = Temp.count

	def __repr__(self):
		return "t" + self.number

class Unary(Op):
	def __init__(self, token, x):
		super(Unary, self).__init__(token, None)
		self.expr = x
		t_type = Type.max(Type.Int, expr.type)
		if not t_type:
			error("type error")

	def gen(self):
		return Unary(self.op, self.expr.reduce())

	def __repr__():
		return self.op + " " + self.expr

class Constant(Expr):
	def __init__(self, token, p):
		if type(token) is int:
			super(Constant, self).__init__(Num(i), Type.Int)
		else:
			super(Constant, self).__init__(token, p)

	def jumping(self, t, f):
		if (self) and t != 0:
			self.emit("goto L" + t)
		elif (not self) and f != 0:
			self.emit("goto L" + f)

Constant.true = Constant(Word.true, Type.Bool)
Constant.false = Constant(Word.false, Type.Bool)

class Logical(Expr):
	def __init__(self, token, x1, x2):
		super(Logical, self).__init__(token, None)
		self.expr1 = x1
		self.expr2 = x2
		t_type = self.check(self.expr2.type, self.expr2.type)
		if not t_type:
			error("type error")

	def check(self, p1, p2):
		if p1 is Type.Bool and p2 is Type.Bool:
			return Type.Bool

	def gen(self):
		f = newlabel()
		a = newlabel()
		temp = Temp(self.type)
		self.jumping(0, f)
		self.emit(temp + " = true")
		self.emit("goto L" + a)
		self.emitlabel(f)
		self.emit(temp + " = false")
		self.emitlabel(a)
		return temp

	def __repr__(self):
		return self.expr1 + " " + self.op + " " + self.expr2

class Or(Logical):
	def __init__(self, token, x1, x2):
		super(Or, self).__init__(token, x1, x2)

	def jumping(self, t, f):
		if t != 0:
			label = t
		else:
			self.newlabel()

		self.expr1.jumping(label, 0)
		self.expr2.jumping(t, f)
		if t == 0:
			self.emitlabel(label)

class And(Logical):
	def __init__(self, token, x1, x2):
		super(And, self).__init__(token, x1, x2)

	def jumping(self, t, f):
		if f != 0:
			label = f
		else:
			self.newlabel()

		self.expr1.jumping(0, label)
		self.expr2.jumping(t, f)
		if f == 0:
			self.emitlabel(label)

class Not(Logical):
	def __init__(self, token, x2):
		super(Not, self).__init__(token, x2, x2)

	def jumping(t, f):
		self.expr2.jumping(f, t)

	def __repr__(self):
		return self.op + " " + self.expr2

class Rel(Logical):
	def __init__(self, x1, x2):
		super(Rel, self).__init__(tok, x1, x2)

	def check(p1, p2):
		if type(p1) is Array or type(p2) is Array:
			return None
		elif p1 == p2:
			return Type.Bool

	def jumping(t, f):
		a = self.expr1.reduce()
		b = self.expr2.reduce()
		test = a + " " + self.op + " " + b
		self.emitjumps(test, t, f)

class Access(Op):
	def __init__(self, a, i, p):
		super(Access, self).__init__(Word("[]", Tag.INDEX), p)
		self.array = a
		self.index = i

	def gen(self):
		return Access(self.array, self.index.reduce(), self.type)

	def jumping(t, f):
		emitjumps(self.reduce().__repr__(), t, f)

	def __repr__(self):
		return self.array + " [ " + self.index.__repr__() + " ]"

class Stmt(Node):
	def gen(b, a):
		self.after = 0

Stmt.Null = Stmt()
Stmt.Enclosing = Stmt.Null

class If(Stmt):
	def __init__(self, x, s):
		self.expr = x
		self.stmt = s
		if self.expr.type is not Type.Bool:
			self.expr.error("boolean required in if")

	def gen(b, a):
		label = newlabel()
		self.expr.jumping(0, a)
		emitlabel(label)
		self.stmt.gen(label, a)

class Else(Stmt):
	def __init__(self, x, s1, s2):
		self.expr = x
		self.stmt1 = s1
		self.stmt2 = s2
		if self.expr.type is not Type.Bool:
			self.expr.error("boolean required in if")

	def gen(b, a):
		label1 = newlabel()
		label2 = newlabel()
		self.expr.jumping(0, label2)
		self.emitlabel(label1)
		self.stmt.gen(label1, a)
		self.emit("goto L" + a)
		self.emitlabel(label2)
		self.stmt2.gen(label2, a)

class While(Stmt):
	def __init__(self):
		self.expr = None
		self.stmt = None

	def initialize(x, s):
		self.expr = x
		self.stmt = s
		if self.expr.type is not Type.Bool:
			self.expr.error("boolean required in while")

	def gen(b, a):
		self.after = a
		self.expr.jumping(0, a)
		label = newlabel()
		self.emitlabel(label)
		self.stmt.gen(label, b)
		self.emit("goto L" + b)

class Do(Stmt):
	def __init__(self):
		self.expr = None
		self.stmt = None

	def initialize(s, x):
		self.expr = x
		self.stmt = s
		if self.expr.type is not Type.Bool:
			self.expr.error("boolean required in do")

	def gen(b, a):
		self.after = a
		label = newlabel()
		self.stmt.gen(b, label)
		self.emitlabel(label)
		self.expr.jumping(b, 0)

class Set(Stmt):
	def __init__(self, i, x):
		self.id = i
		self.expr = x
		if not self.check(self.id.type, self.expr.type):
			self.error("type error")

	def check(self, p1, p2):
		if Type.numeric(p1) and Type.numeric(p2):
			return p2
		elif p1 is Type.Bool and p2 is Type.Bool:
			return p2

	def gen(b, a):
		self.emit(self.id + " = " + self.expr.gen())

class SetElem(Stmt):
	def __init__(self, x, y):
		self.array = x.array
		self.index = x.index
		self.expr = y
		if self.check(x.type, expr.type):
			self.error("type error")

	def check(self, p1, p2):
		if type(p1) is Array or type(p2) is Array:
			return None
		elif p1 is p2:
			return p2
		elif Type.numeric(p1) and Type.numeric(p2):
			return p2

	def gen(b, a):
		s1 = self.index.reduce()
		s2 = self.expr.reduce()
		self.emit(self.array + " [ " + s1 + "] = " + s2)

class Seq(Stmt):
	def __init__(s1, s2):
		self.stmt1 = s1
		self.stmt2 = s2

	def gen(b, a):
		if self.stmt1 == Stmt.Null:
			self.stmt2.gen(b, a)
		elif self.stmt2 == Stmt.Null:
			self.stmt1.gen(b, a)
		else:
			label = newlabel()
			self.stmt1.gen(b, label)
			self.emitlabel(label)
			self.stmt2.gen(label, a)

class Break(Stmt):
	def __init__(self):
		if Stmt.Enclosing:
			error("unenclosed break")
			self.stmt = Stmt.Enclosing

	def gen(b, a):
		self.emit("goto L" + self.stmt.after)

#
# class Parser:
# 	def __main__:
# 		scanner = Scanner(sysarg[-1])
