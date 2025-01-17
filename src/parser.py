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
            if token.value == 'arg':
                return self.parse_variable_declaration()
            elif token.value == 'fn':
                return self.parse_function_declaration()
            elif token.value == 'lambda':
                return self.parse_lambda_declaration()
            elif token.value == 'return':
                return self.parse_return_statement()
            elif token.value == 'prtoc':
                return self.parse_print_statement()
            elif token.value == 'if':
                return self.parse_if_statement()
            elif token.value == 'while':
                return self.parse_while_statement()
            elif token.value == 'for':
                return self.parse_for_statement()
            elif token.value == 'try':
                return self.parse_try_catch()
            elif token.value == 'throw':
                return self.parse_throw()
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
        left = self.parse_term()
        
        while (self.pos < len(self.tokens) and 
               self.current_token().type in ['PLUS', 'MINUS', 'EQUALS', 'NOT_EQUALS', 
                                          'LESS_THAN', 'GREATER_THAN', 'LESS_EQUALS', 
                                          'GREATER_EQUALS', 'AND', 'OR']):
            operator = self.current_token().value
            self.pos += 1
            right = self.parse_term()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
        
        return left
        
    def parse_term(self):
        left = self.parse_factor()
        
        while (self.pos < len(self.tokens) and 
               self.current_token().type in ['MULTIPLY', 'DIVIDE', 'MODULO']):
            operator = self.current_token().value
            self.pos += 1
            right = self.parse_factor()
            left = {'type': 'binary_op', 'operator': operator, 'left': left, 'right': right}
        
        return left
        
    def parse_factor(self):
        token = self.current_token()
        
        if token.type == 'PLUS' or token.type == 'MINUS':
            operator = token.value
            self.pos += 1
            operand = self.parse_factor()
            return {'type': 'unary_op', 'operator': operator, 'operand': operand}
            
        return self.parse_primary()
        
    def parse_primary(self):
        token = self.current_token()
        
        if token.type == 'NUMBER':
            self.pos += 1
            return {'type': 'number', 'value': float(token.value)}
            
        elif token.type == 'STRING':
            self.pos += 1
            return {'type': 'string', 'value': token.value}
            
        elif token.type == 'IDENTIFIER':
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'LPAREN':
                return self.parse_function_call()
            else:
                self.pos += 1
                return {'type': 'variable', 'name': token.value}
                
        elif token.type == 'LPAREN':
            self.pos += 1
            expr = self.parse_expression()
            if self.current_token().type != 'RPAREN':
                raise SyntaxError(f"Expected RPAREN, got {self.current_token().type}")
            self.pos += 1
            return expr
            
        elif token.type == 'LBRACKET':
            return self.parse_array_literal()
            
        elif token.type == 'KEYWORD':
            if token.value == 'lambda':
                return self.parse_lambda_declaration()
            elif token.value in ['true', 'false']:
                self.pos += 1
                return {'type': 'boolean', 'value': token.value == 'true'}
                
        raise SyntaxError(f"Unexpected token {token.type} at line {token.line}, column {token.column}")

    def parse_variable_declaration(self):
        self.consume('KEYWORD')  # consume 'arg'
        name = self.consume('IDENTIFIER').value
        
        # Type annotation is optional
        if self.current_token().type == 'COLON':
            self.consume('COLON')
            type_token = self.consume('KEYWORD').value
        else:
            type_token = None
            
        self.consume('ASSIGN')
        
        # Handle lambda functions
        if self.current_token().type == 'KEYWORD' and self.current_token().value == 'lambda':
            value = self.parse_lambda_declaration()
        else:
            value = self.parse_expression()
            
        if self.pos < len(self.tokens) and self.current_token().type == 'SEMICOLON':
            self.consume('SEMICOLON')
            
        return {'type': 'var_declaration', 'name': name, 'var_type': type_token, 'value': value}

    def parse_function_declaration(self):
        self.consume('KEYWORD')  # consume 'fn'
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        params = []
        
        if self.current_token().type != 'RPAREN':
            # Parse first parameter
            param_name = self.consume('IDENTIFIER').value
            self.consume('COLON')
            param_type = self.consume('KEYWORD').value
            params.append({'name': param_name, 'type': param_type})
            
            # Parse additional parameters
            while self.current_token().type == 'COMMA':
                self.consume('COMMA')
                param_name = self.consume('IDENTIFIER').value
                self.consume('COLON')
                param_type = self.consume('KEYWORD').value
                params.append({'name': param_name, 'type': param_type})
                
        self.consume('RPAREN')
        
        # Parse return type
        return_type = None
        if self.current_token().type == 'KEYWORD':
            return_type = self.consume('KEYWORD').value
            
        self.consume('LBRACE')
        body = []
        while self.current_token().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        
        return {'type': 'function_declaration', 'name': name, 'params': params, 'return_type': return_type, 'body': body}

    def parse_function_call(self):
        name = self.consume('IDENTIFIER').value
        args = []
        
        self.consume('LPAREN')
        if self.current_token().type != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token().type == 'COMMA':
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
        self.consume('KEYWORD')  # consume 'prtoc'
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
        self.consume('LBRACKET')
        elements = []
        
        if self.current_token().type != 'RBRACKET':
            elements.append(self.parse_expression())
            while self.current_token().type == 'COMMA':
                self.consume('COMMA')
                elements.append(self.parse_expression())
                
        self.consume('RBRACKET')
        return {'type': 'array_literal', 'elements': elements}

    def parse_lambda_declaration(self):
        self.consume('KEYWORD')  # consume 'lambda'
        self.consume('LPAREN')
        params = []
        if self.current_token().type != 'RPAREN':
            name = self.consume('IDENTIFIER').value
            self.consume('COLON')
            type_token = self.consume('KEYWORD').value
            params.append({'name': name, 'type': type_token})
            while self.current_token().type == 'COMMA':
                self.consume('COMMA')
                name = self.consume('IDENTIFIER').value
                self.consume('COLON')
                type_token = self.consume('KEYWORD').value
                params.append({'name': name, 'type': type_token})
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while self.current_token().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        return {'type': 'lambda', 'params': params, 'body': body}

    def parse_try_catch(self):
        self.consume('KEYWORD')  # consume 'try'
        self.consume('LBRACE')
        try_body = []
        while self.current_token().type != 'RBRACE':
            try_body.append(self.parse_statement())
        self.consume('RBRACE')
        
        self.consume('KEYWORD')  # consume 'catch'
        error_var = self.consume('IDENTIFIER').value
        
        self.consume('LBRACE')
        catch_body = []
        while self.current_token().type != 'RBRACE':
            catch_body.append(self.parse_statement())
        self.consume('RBRACE')
        
        return {'type': 'try_catch', 'try_body': try_body, 'catch_var': error_var, 'catch_body': catch_body}

    def parse_throw(self):
        self.consume('KEYWORD')  # consume 'throw'
        value = self.parse_expression()
        if self.current_token().type == 'SEMICOLON':
            self.consume('SEMICOLON')
        return {'type': 'throw', 'value': value}

    def parse_parameter(self):
        name = self.consume('IDENTIFIER').value
        self.consume('COLON')
        type_token = self.consume('KEYWORD').value
        return {'name': name, 'type': type_token}

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
