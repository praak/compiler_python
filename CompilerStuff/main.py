import sys
from scanner import Scanner
from parser import Parser

def main():
    lex = Scanner("test.cpp")
    parse = Parser(lex)
    parse.program()

if __name__ == "__main__":
    main()
