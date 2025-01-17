from typing import List, Dict, Any
from .token import Token

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        
    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            statements.append(self.parse_statement())
        return statements
        
    def parse_statement(self):
        token = self.current_token()
        if token.type == 'KEYWORD':
            if token.value == 'var':
                return self.parse_variable_declaration()
            elif token.value == 'func':
                return self.parse_function_declaration()
            elif token.value == 'return':
                return self.parse_return_statement()
            elif token.value == 'print':
                return self.parse_print_statement()
            elif token.value == 'if':
                return self.parse_if_statement()
            elif token.value == 'while':
                return self.parse_while_statement()
        elif token.type == 'IDENTIFIER':
            # Handle assignment to existing variable
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'ASSIGN':
                name = token.value
                self.pos += 1  # Skip identifier
                self.consume('ASSIGN')
                value = self.parse_expression()
                self.consume('SEMICOLON')
                return {'type': 'assignment', 'name': name, 'value': value}
        return self.parse_expression()

    def parse_expression(self):
        return self.parse_logical_or()
        
    def parse_logical_or(self):
        left = self.parse_logical_and()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == 'OR':
            operator = self.tokens[self.pos].value
            self.pos += 1
            right = self.parse_logical_and()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
            
        return left
        
    def parse_logical_and(self):
        left = self.parse_equality()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == 'AND':
            operator = self.tokens[self.pos].value
            self.pos += 1
            right = self.parse_equality()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
            
        return left
        
    def parse_equality(self):
        left = self.parse_comparison()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ['EQUALS', 'NOT_EQUALS']:
            operator = self.tokens[self.pos].value
            self.pos += 1
            right = self.parse_comparison()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
            
        return left
        
    def parse_comparison(self):
        left = self.parse_additive()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ['LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL']:
            operator = self.tokens[self.pos].value
            self.pos += 1
            right = self.parse_additive()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
            
        return left
        
    def parse_additive(self):
        left = self.parse_multiplicative()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ['PLUS', 'MINUS']:
            operator = self.tokens[self.pos].value
            self.pos += 1
            right = self.parse_multiplicative()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
            
        return left
        
    def parse_multiplicative(self):
        left = self.parse_primary()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ['MULTIPLY', 'DIVIDE', 'MODULO']:
            operator = self.tokens[self.pos].value
            self.pos += 1
            right = self.parse_primary()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
            
        return left
        
    def parse_primary(self):
        token = self.current_token()
        if token.type == 'NUMBER':
            self.pos += 1
            return {'type': 'number', 'value': float(token.value)}
        elif token.type == 'STRING':
            self.pos += 1
            # Remove the quotes from the string value
            value = token.value[1:-1] if token.value.startswith('"') and token.value.endswith('"') else token.value
            return {'type': 'string', 'value': value}
        elif token.type == 'KEYWORD':
            if token.value in ['true', 'false']:
                self.pos += 1
                return {'type': 'boolean', 'value': token.value == 'true'}
            elif token.value == 'if':
                return self.parse_conditional_expression()
        elif token.type == 'IDENTIFIER':
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'LPAREN':
                self.pos -= 1
                return self.parse_function_call()
            return {'type': 'variable', 'name': token.value}
        elif token.type == 'LPAREN':
            self.pos += 1
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token {token.type} at line {token.line}, column {token.column}")

    def parse_variable_declaration(self):
        self.consume('KEYWORD')  # consume 'var'
        name = self.consume('IDENTIFIER').value
        self.consume('COLON')
        type_token = self.consume('KEYWORD')  # Changed from IDENTIFIER to KEYWORD for type names
        self.consume('ASSIGN')
        value = self.parse_expression()
        self.consume('SEMICOLON')
        return {'type': 'var_declaration', 'name': name, 'var_type': type_token.value, 'value': value}

    def parse_function_declaration(self):
        self.consume('KEYWORD')  # consume 'func'
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        params = []
        
        while self.current_token().type != 'RPAREN':
            if params:
                self.consume('COMMA')
            param_name = self.consume('IDENTIFIER').value
            self.consume('COLON')
            param_type = self.consume('KEYWORD').value  # Changed from IDENTIFIER to KEYWORD
            params.append({'name': param_name, 'type': param_type})
            
        self.consume('RPAREN')
        return_type = self.consume('KEYWORD').value  # Changed from IDENTIFIER to KEYWORD
        
        self.consume('LBRACE')
        body = []
        while self.current_token().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        
        return {'type': 'function_declaration', 'name': name, 'params': params, 
                'return_type': return_type, 'body': body}

    def parse_function_call(self):
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        args = []
        
        while self.current_token().type != 'RPAREN':
            if args:
                self.consume('COMMA')
            args.append(self.parse_expression())
            
        self.consume('RPAREN')
        return {'type': 'function_call', 'name': name, 'arguments': args}

    def parse_return_statement(self):
        self.consume('KEYWORD')  # consume 'return'
        value = self.parse_expression()
        self.consume('SEMICOLON')
        return {'type': 'return', 'value': value}

    def parse_print_statement(self):
        self.consume('KEYWORD')  # consume 'print'
        self.consume('LPAREN')
        args = []
        
        while self.current_token().type != 'RPAREN':
            if args:
                self.consume('COMMA')
            args.append(self.parse_expression())
            
        self.consume('RPAREN')
        self.consume('SEMICOLON')
        return {'type': 'print', 'arguments': args}

    def parse_if_statement(self):
        self.consume('KEYWORD')  # consume 'if'
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        
        self.consume('LBRACE')
        then_branch = []
        while self.current_token().type != 'RBRACE':
            then_branch.append(self.parse_statement())
        self.consume('RBRACE')
        
        else_branch = []
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == 'KEYWORD' and self.tokens[self.pos].value == 'else':
            self.consume('KEYWORD')  # consume 'else'
            self.consume('LBRACE')
            while self.current_token().type != 'RBRACE':
                else_branch.append(self.parse_statement())
            self.consume('RBRACE')
            
        return {'type': 'if', 'condition': condition, 'then': then_branch, 'else': else_branch}

    def parse_while_statement(self):
        self.consume('KEYWORD')  # consume 'while'
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        
        self.consume('LBRACE')
        body = []
        while self.current_token().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        
        return {'type': 'while', 'condition': condition, 'body': body}

    def parse_conditional_expression(self):
        self.consume('KEYWORD')  # consume 'if'
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        
        then_expr = self.parse_expression()
        
        if self.current_token().type == 'KEYWORD' and self.current_token().value == 'else':
            self.consume('KEYWORD')  # consume 'else'
            else_expr = self.parse_expression()
        else:
            else_expr = None
            
        return {'type': 'conditional', 'condition': condition, 'then': then_expr, 'else': else_expr}

    def current_token(self) -> Token:
        if self.pos >= len(self.tokens):
            raise SyntaxError("Unexpected end of input")
        return self.tokens[self.pos]
        
    def consume(self, expected_type: str) -> Token:
        token = self.current_token()
        if token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token
