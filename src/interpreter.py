from typing import Dict, Any, Optional

class Interpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}
        
    def evaluate(self, ast):
        result = None
        for node in ast:
            result = self.evaluate_node(node)
        return result
        
    def evaluate_node(self, node):
        if not isinstance(node, dict):
            return node
            
        node_type = node.get('type')
        
        if node_type == 'number':
            return node['value']
            
        elif node_type == 'string':
            return str(node['value'])  # Ensure string type for concatenation
            
        elif node_type == 'boolean':
            return node['value']
            
        elif node_type == 'conditional':
            condition = self.evaluate_node(node['condition'])
            if condition:
                return self.evaluate_node(node['then'])
            elif node['else'] is not None:
                return self.evaluate_node(node['else'])
            else:
                return None
            
        elif node_type == 'variable':
            if node['name'] not in self.variables:
                raise NameError(f"Variable '{node['name']}' is not defined")
            return self.variables[node['name']]
            
        elif node_type == 'binary_op':
            left = self.evaluate_node(node['left'])
            
            # Short-circuit evaluation for logical operators
            if node['operator'] == '&&':
                return left and self.evaluate_node(node['right'])
            elif node['operator'] == '||':
                return left or self.evaluate_node(node['right'])
                
            right = self.evaluate_node(node['right'])
            
            # Handle string concatenation
            if node['operator'] == '+':
                if isinstance(left, str) or isinstance(right, str):
                    # Convert numbers to strings with proper formatting
                    if isinstance(left, (int, float)):
                        left = str(int(left) if left.is_integer() else left)
                    if isinstance(right, (int, float)):
                        right = str(int(right) if right.is_integer() else right)
                    return str(left) + str(right)
                return left + right
                
            elif node['operator'] == '-':
                return left - right
            elif node['operator'] == '*':
                return left * right
            elif node['operator'] == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right
            elif node['operator'] == '%':
                if right == 0:
                    raise ZeroDivisionError("Modulo by zero")
                return left % right
            elif node['operator'] == '==':
                return left == right
            elif node['operator'] == '!=':
                return left != right
            elif node['operator'] == '<':
                return left < right
            elif node['operator'] == '>':
                return left > right
            elif node['operator'] == '<=':
                return left <= right
            elif node['operator'] == '>=':
                return left >= right
            
        elif node_type == 'var_declaration':
            value = self.evaluate_node(node['value'])
            self.variables[node['name']] = value
            return value
            
        elif node_type == 'assignment':
            if node['name'] not in self.variables:
                raise NameError(f"Variable '{node['name']}' is not defined")
            value = self.evaluate_node(node['value'])
            self.variables[node['name']] = value
            return value
            
        elif node_type == 'function_declaration':
            self.functions[node['name']] = node
            return None
            
        elif node_type == 'function_call':
            if node['name'] == 'print':
                args = [self.evaluate_node(arg) for arg in node['arguments']]
                print(*args)
                return None
                
            if node['name'] not in self.functions:
                raise NameError(f"Function '{node['name']}' is not defined")
                
            func = self.functions[node['name']]
            if len(node['arguments']) != len(func['params']):
                raise TypeError(f"Function '{node['name']}' expects {len(func['params'])} arguments")
                
            # Create new scope for function
            old_variables = self.variables.copy()
            
            # Bind parameters to arguments
            for param, arg in zip(func['params'], node['arguments']):
                self.variables[param['name']] = self.evaluate_node(arg)
                
            # Execute function body
            result = None
            for statement in func['body']:
                result = self.evaluate_node(statement)
                if isinstance(result, dict) and result.get('type') == 'return':
                    result = self.evaluate_node(result['value'])
                    break
                    
            # Restore old scope
            self.variables = old_variables
            return result
            
        elif node_type == 'if':
            condition = self.evaluate_node(node['condition'])
            if condition:
                for statement in node['then']:
                    result = self.evaluate_node(statement)
                return result
            else:
                for statement in node['else']:
                    result = self.evaluate_node(statement)
                return result
                
        elif node_type == 'while':
            result = None
            while self.evaluate_node(node['condition']):
                for statement in node['body']:
                    result = self.evaluate_node(statement)
            return result
            
        elif node_type == 'return':
            return node
            
        elif node_type == 'print':
            args = [self.evaluate_node(arg) for arg in node['arguments']]
            print(*args)
            return None
