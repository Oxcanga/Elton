from typing import List
from .token import Token

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            # Skip whitespace
            if char.isspace():
                if char == '\n':
                    self.line += 1
                    self.column = 0
                self.pos += 1
                self.column += 1
                continue
                
            # Handle comments
            if char == '/' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue
                
            # Handle string interpolation and regular strings
            if char == '"':
                string = ''
                start_col = self.column
                self.pos += 1  # Skip opening quote
                self.column += 1
                
                while self.pos < len(self.source) and self.source[self.pos] != '"':
                    if self.source[self.pos] == '\\':
                        self.pos += 1
                        self.column += 1
                        if self.pos >= len(self.source):
                            raise SyntaxError(f"Unterminated string at line {self.line}, column {start_col}")
                        string += {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(self.source[self.pos], self.source[self.pos])
                    elif self.source[self.pos] == '$' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '{':
                        # Handle string interpolation
                        if string:
                            self.tokens.append(Token('STRING', '"' + string + '"', self.line, start_col))
                            self.tokens.append(Token('PLUS', '+', self.line, self.column))
                            string = ''
                            
                        self.pos += 2  # Skip ${
                        self.column += 2
                        
                        # Parse the expression inside ${}
                        expr_start = self.pos
                        brace_count = 1
                        while self.pos < len(self.source) and brace_count > 0:
                            if self.source[self.pos] == '{':
                                brace_count += 1
                            elif self.source[self.pos] == '}':
                                brace_count -= 1
                            self.pos += 1
                            self.column += 1
                            
                        if brace_count > 0:
                            raise SyntaxError(f"Unterminated string interpolation at line {self.line}, column {start_col}")
                            
                        # Create a new lexer for the interpolated expression
                        expr_lexer = Lexer(self.source[expr_start:self.pos-1])
                        expr_tokens = expr_lexer.tokenize()
                        
                        # Add string conversion
                        self.tokens.append(Token('LPAREN', '(', self.line, self.column))
                        self.tokens.extend(expr_tokens)
                        self.tokens.append(Token('RPAREN', ')', self.line, self.column))
                        
                        self.tokens.append(Token('PLUS', '+', self.line, self.column))
                        continue
                    else:
                        string += self.source[self.pos]
                    self.pos += 1
                    self.column += 1
                    
                if self.pos >= len(self.source):
                    raise SyntaxError(f"Unterminated string at line {self.line}, column {start_col}")
                    
                self.pos += 1  # Skip closing quote
                self.column += 1
                if string:
                    self.tokens.append(Token('STRING', '"' + string + '"', self.line, start_col))
                continue
                
            # Multi-character operators
            two_char_ops = {
                '==': 'EQUALS',
                '!=': 'NOT_EQUALS',
                '<=': 'LESS_EQUAL',
                '>=': 'GREATER_EQUAL',
                '&&': 'AND',
                '||': 'OR',
                '..': 'RANGE'  # Added range operator for array slicing
            }
            
            if self.pos + 1 < len(self.source):
                two_chars = self.source[self.pos:self.pos + 2]
                if two_chars in two_char_ops:
                    self.tokens.append(Token(two_char_ops[two_chars], two_chars, self.line, self.column))
                    self.pos += 2
                    self.column += 2
                    continue
                    
            # Numbers
            if char.isdigit() or (char == '-' and self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit()):
                num = ''
                start_col = self.column
                if char == '-':
                    num += char
                    self.pos += 1
                    self.column += 1
                    char = self.source[self.pos]
                while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
                    # Check for range operator
                    if self.pos + 1 < len(self.source) and self.source[self.pos:self.pos + 2] == '..':
                        break
                    num += self.source[self.pos]
                    self.pos += 1
                    self.column += 1
                self.tokens.append(Token('NUMBER', num, self.line, start_col))
                continue
                
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                ident = ''
                start_col = self.column
                while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                    ident += self.source[self.pos]
                    self.pos += 1
                    self.column += 1
                    
                # Check if it's a keyword
                keywords = {'var', 'func', 'if', 'else', 'while', 'return', 'print', 'true', 'false', 
                          'and', 'or', 'not', 'string', 'int', 'bool', 'float', 'array', 'for', 'in',
                          'try', 'catch', 'throw', 'lambda'}
                token_type = 'KEYWORD' if ident in keywords else 'IDENTIFIER'
                self.tokens.append(Token(token_type, ident, self.line, start_col))
                continue
                
            # Single-character operators and punctuation
            operators = {
                '+': 'PLUS',
                '-': 'MINUS',
                '*': 'MULTIPLY',
                '/': 'DIVIDE',
                '%': 'MODULO',
                '=': 'ASSIGN',
                '<': 'LESS',
                '>': 'GREATER',
                '!': 'NOT',
                '(': 'LPAREN',
                ')': 'RPAREN',
                '{': 'LBRACE',
                '}': 'RBRACE',
                '[': 'LBRACKET',
                ']': 'RBRACKET',
                ':': 'COLON',
                ';': 'SEMICOLON',
                ',': 'COMMA',
                '.': 'DOT'
            }
            
            if char in operators:
                self.tokens.append(Token(operators[char], char, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
                
            raise SyntaxError(f"Invalid character '{char}' at line {self.line}, column {self.column}")
            
        return self.tokens
