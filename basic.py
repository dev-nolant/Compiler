from string_with_arrows import *

INT_ = 'INT'
FLOAT_ = 'FLOAT'
PLUS_ = 'PlUS'
MINUS_ = 'MINUS'
MUL_ = 'MUL'
DIV_ = 'DIV'
LPAREN_ = 'LPAREN'
RPAREN_ = 'RPAREN'

DIGITS = '0123456789'
#################################
# START #
#################################
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.error_name = error_name
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details       
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
#Errors
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal CHAR ", details)
class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Invalid Syntax", details)
#Position set
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.fn = fn
        self.ftxt = ftxt
        self.idx = idx
        self.ln = ln
        self.col = col
    def advance(self, current_char):
        self.idx += 1
        self.col = 0
        
        if current_char == '\n':
            self.ln +=1
            self.col = 0
        return self
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)
#Token Gen
class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
#Daddy lexer
class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    def gene_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(PLUS_))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(MINUS_))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(MUL_))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(DIV_))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(LPAREN_))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(RPAREN_))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        return tokens, None
    def make_number(self):
        num_str =''
        dot_count = 0
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(INT_, int(num_str))
        else:
            return Token(FLOAT_, float(num_str))
#Nodes
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
    def __repr__(self):
        return f'{self.tok}'
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.right_node = right_node
        self.op_tok = op_tok
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
#Mama parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1 #IMPORTANT
        self.advance()
    def advance(self):
        self.tok_idx +=1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    def parse(self):
        res = self.expr()
        return res
    def factor(self):
        tok = self.current_tok
        if tok.type in (INT_, FLOAT_):
            self.advance()
            return NumberNode(tok)
    def term(self):
        return self.bin_op(self.factor, (MUL_, DIV_))
    def expr(self):
        return self.bin_op(self.term, (PLUS_, MINUS_))
    def bin_op(self, function, ops):
        left = function()
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            self.advance()
            right = function()
            left = BinOpNode(left, op_tok, right)
        return left


#Bruh run
def run(fn, test_TXT):
    lexer = Lexer(fn, test_TXT)
    tokens, error = lexer.gene_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast, None