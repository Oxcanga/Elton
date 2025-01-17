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
            elif token.value == 'for':
                return self.parse_for_statement()
        elif token.type == 'IDENTIFIER':
            # Handle assignment to existing variable
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'ASSIGN':
                name = token.value
                self.pos += 1  # Skip identifier
                self.consume('ASSIGN')
                value = self.parse_expression()
                if self.pos < len(self.tokens) and self.current_token().type == 'SEMICOLON':
                    self.consume('SEMICOLON')
                return {'type': 'assignment', 'name': name, 'value': value}
            # Handle function calls as statements
            elif self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'LPAREN':
                expr = self.parse_function_call()
                if self.pos < len(self.tokens) and self.current_token().type == 'SEMICOLON':
                    self.consume('SEMICOLON')
                return expr
        return self.parse_expression()

    def parse_expression(self):
        return self.parse_logical_or()
        
    def parse_logical_or(self):
        expr = self.parse_logical_and()
        while self.pos < len(self.tokens) and self.current_token().type == 'OR':
            operator = self.consume('OR').value
            right = self.parse_logical_and()
            expr = {'type': 'binary_op', 'operator': operator, 'left': expr, 'right': right}
        return expr
        
    def parse_logical_and(self):
        expr = self.parse_equality()
        while self.pos < len(self.tokens) and self.current_token().type == 'AND':
            operator = self.consume('AND').value
            right = self.parse_equality()
            expr = {'type': 'binary_op', 'operator': operator, 'left': expr, 'right': right}
        return expr
        
    def parse_equality(self):
        expr = self.parse_relational()
        while self.pos < len(self.tokens) and self.current_token().type in ['EQUALS', 'NOT_EQUALS']:
            operator = self.consume(self.current_token().type).value
            right = self.parse_relational()
            expr = {'type': 'binary_op', 'operator': operator, 'left': expr, 'right': right}
        return expr
        
    def parse_relational(self):
        expr = self.parse_additive()
        while self.pos < len(self.tokens) and self.current_token().type in ['LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL']:
            operator = self.consume(self.current_token().type).value
            right = self.parse_additive()
            expr = {'type': 'binary_op', 'operator': operator, 'left': expr, 'right': right}
        return expr
        
    def parse_additive(self):
        expr = self.parse_multiplicative()
        while self.pos < len(self.tokens) and self.current_token().type in ['PLUS', 'MINUS']:
            operator = self.consume(self.current_token().type).value
            right = self.parse_multiplicative()
            expr = {'type': 'binary_op', 'operator': operator, 'left': expr, 'right': right}
        return expr
        
    def parse_multiplicative(self):
        expr = self.parse_primary()
        while self.pos < len(self.tokens) and self.current_token().type in ['MULTIPLY', 'DIVIDE', 'MODULO']:
            operator = self.consume(self.current_token().type).value
            right = self.parse_primary()
            expr = {'type': 'binary_op', 'operator': operator, 'left': expr, 'right': right}
        return expr
        
    def parse_primary(self):
        token = self.current_token()
        
        if token.type == 'NUMBER':
            self.pos += 1
            return {'type': 'number', 'value': float(token.value)}
        elif token.type == 'STRING':
            self.pos += 1
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
            if self.pos < len(self.tokens):
                next_token = self.tokens[self.pos]
                if next_token.type == 'LPAREN':
                    self.pos -= 1
                    return self.parse_function_call()
                elif next_token.type == 'LBRACKET':
                    self.consume('LBRACKET')
                    index = self.parse_expression()
                    self.consume('RBRACKET')
                    return {'type': 'array_access', 'array': token.value, 'index': index}
            return {'type': 'variable', 'name': token.value}
        elif token.type == 'LPAREN':
            self.pos += 1
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        elif token.type == 'LBRACKET':
            return self.parse_array_literal()
            
        raise SyntaxError(f"Unexpected token {token.type} at line {token.line}, column {token.column}")

    def parse_variable_declaration(self):
        self.consume('KEYWORD')  # consume 'var'
        name = self.consume('IDENTIFIER').value
        self.consume('COLON')
        type_token = self.consume('KEYWORD')  # Changed from IDENTIFIER to KEYWORD for type names
        self.consume('ASSIGN')
        
        # Handle array literals
        if self.current_token().type == 'LBRACKET':
            value = self.parse_array_literal()
        else:
            value = self.parse_expression()
            
        if self.pos < len(self.tokens) and self.current_token().type == 'SEMICOLON':
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
        if self.pos < len(self.tokens) and self.current_token().type == 'SEMICOLON':
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
        if self.pos < len(self.tokens) and self.current_token().type == 'SEMICOLON':
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

    def parse_for_statement(self):
        self.consume('KEYWORD')  # consume 'for'
        iterator = self.consume('IDENTIFIER').value
        self.consume('KEYWORD')  # consume 'in'
        
        # Parse the iterable (either a range or an array)
        start = self.parse_expression()
        
        # If we see a range operator, this is a range-based for loop
        if self.current_token().type == 'RANGE':
            self.consume('RANGE')
            end = self.parse_expression()
            
            # Create a range node with properly typed start and end values
            if isinstance(start, dict) and start.get('type') == 'number':
                start_val = start
            elif isinstance(start, dict) and start.get('type') == 'variable':
                start_val = start  # Keep variable reference as is
            else:
                start_val = {'type': 'number', 'value': float(start)}
                
            if isinstance(end, dict) and end.get('type') == 'number':
                end_val = end
            elif isinstance(end, dict) and end.get('type') == 'variable':
                end_val = end  # Keep variable reference as is
            else:
                end_val = {'type': 'number', 'value': float(end)}
                
            iterable = {'type': 'range', 'start': start_val, 'end': end_val}
        else:
            # This is an array-based for loop
            iterable = start
            
        self.consume('LBRACE')
        body = []
        while self.current_token().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        
        return {'type': 'for', 'iterator': iterator, 'iterable': iterable, 'body': body}

    def parse_array_literal(self):
        elements = []
        self.consume('LBRACKET')
        
        if self.current_token().type != 'RBRACKET':
            elements.append(self.parse_expression())
            while self.current_token().type == 'COMMA':
                self.consume('COMMA')
                elements.append(self.parse_expression())
            
        self.consume('RBRACKET')
        return {'type': 'array', 'elements': elements}

    def parse_array_access(self, array_name):
        self.consume('LBRACKET')
        index = self.parse_expression()
        self.consume('RBRACKET')
        return {'type': 'array_access', 'array': array_name, 'index': index}

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
