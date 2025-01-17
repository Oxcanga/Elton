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
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
                continue
                
            # Skip comments
            if char == '/' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue
                
            # Handle string literals
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
                        # Add the string part before interpolation
                        if string:
                            self.tokens.append(Token('STRING', f'"{string}"', self.line, start_col))
                            self.tokens.append(Token('PLUS', '+', self.line, self.column))
                        
                        # Skip ${
                        self.pos += 2
                        self.column += 2
                        
                        # Parse the interpolated expression
                        start = self.pos
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
                        
                        # Convert the interpolated expression to string
                        expr = self.source[start:self.pos-1].strip()
                        self.tokens.append(Token('IDENTIFIER', expr, self.line, start_col))
                        
                        # Add string concatenation operator
                        self.tokens.append(Token('PLUS', '+', self.line, self.column))
                        string = ''  # Reset string buffer
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
                    self.tokens.append(Token('STRING', f'"{string}"', self.line, start_col))
                continue
                
            # Multi-character operators
            if char == '=' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '=':
                self.tokens.append(Token('EQUALS', '==', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
            elif char == '!' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '=':
                self.tokens.append(Token('NOT_EQUALS', '!=', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
            elif char == '<' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '=':
                self.tokens.append(Token('LESS_EQUALS', '<=', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
            elif char == '>' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '=':
                self.tokens.append(Token('GREATER_EQUALS', '>=', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
            elif char == '&' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '&':
                self.tokens.append(Token('AND', '&&', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
            elif char == '|' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '|':
                self.tokens.append(Token('OR', '||', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
                
            # Single-character operators
            elif char in '+-*/%':
                self.tokens.append(Token({'+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE', '%': 'MODULO'}[char], char, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == '<':
                self.tokens.append(Token('LESS_THAN', '<', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == '>':
                self.tokens.append(Token('GREATER_THAN', '>', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == '=':
                self.tokens.append(Token('ASSIGN', '=', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
                
            # Parentheses and braces
            elif char == '(':
                self.tokens.append(Token('LPAREN', '(', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == ')':
                self.tokens.append(Token('RPAREN', ')', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == '{':
                self.tokens.append(Token('LBRACE', '{', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == '}':
                self.tokens.append(Token('RBRACE', '}', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == '[':
                self.tokens.append(Token('LBRACKET', '[', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == ']':
                self.tokens.append(Token('RBRACKET', ']', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
                
            # Other punctuation
            elif char == ',':
                self.tokens.append(Token('COMMA', ',', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == ':':
                self.tokens.append(Token('COLON', ':', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == '.':
                self.tokens.append(Token('DOT', '.', self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
            elif char == ';':
                self.tokens.append(Token('SEMICOLON', ';', self.line, self.column))
                self.pos += 1
                self.column += 1
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
                keywords = {'arg', 'fn', 'if', 'else', 'while', 'return', 'print', 'true', 'false', 
                          'and', 'or', 'not', 'string', 'int', 'bool', 'float', 'array', 'for', 'in',
                          'try', 'catch', 'throw', 'lambda'}
                token_type = 'KEYWORD' if ident in keywords else 'IDENTIFIER'
                self.tokens.append(Token(token_type, ident, self.line, start_col))
                continue
                
            raise SyntaxError(f"Invalid character '{char}' at line {self.line}, column {self.column}")
            
        return self.tokens
