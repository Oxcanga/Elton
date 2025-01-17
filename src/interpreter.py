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
            if node['operator'] == '+' and (isinstance(left, str) or isinstance(right, str)):
                # Convert numbers to strings with proper formatting
                if isinstance(left, (int, float)):
                    left = str(int(left) if left.is_integer() else left)
                if isinstance(right, (int, float)):
                    right = str(int(right) if right.is_integer() else right)
                return str(left) + str(right)
            
            # Handle numeric operations
            if node['operator'] in ['+', '-', '*', '/', '%'] and (not isinstance(left, (int, float)) or not isinstance(right, (int, float))):
                raise TypeError(f"Cannot perform {node['operator']} operation on {type(left)} and {type(right)}")
                
            if node['operator'] == '+':
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
            elif node['operator'] == '<':
                return left < right
            elif node['operator'] == '>':
                return left > right
            elif node['operator'] == '==':
                return left == right
            elif node['operator'] == '!=':
                return left != right
            elif node['operator'] == '<=':
                return left <= right
            elif node['operator'] == '>=':
                return left >= right
            
        elif node_type == 'array':
            elements = [self.evaluate_node(element) for element in node['elements']]
            return elements
            
        elif node_type == 'array_access':
            array = self.evaluate_node({'type': 'variable', 'name': node['array']})
            if array is None:
                raise NameError(f"Variable '{node['array']}' is not defined")
            if not isinstance(array, list):
                raise TypeError(f"Variable '{node['array']}' is not an array")
                
            index = self.evaluate_node(node['index'])
            if not isinstance(index, (int, float)) or not float(index).is_integer():
                raise TypeError("Array index must be an integer")
            index = int(index)
            
            if index < 0 or index >= len(array):
                raise IndexError(f"Array index {index} out of bounds")
            return array[index]
            
        elif node_type == 'var_declaration':
            name = node['name']
            value = self.evaluate_node(node['value'])
            self.variables[name] = value
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
            result = None
            if condition:
                for statement in node['then']:
                    result = self.evaluate_node(statement)
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
            
        elif node_type == 'for':
            iterator_name = node['iterator']
            iterable = self.evaluate_node(node['iterable'])
            
            # Handle range expressions
            if isinstance(iterable, dict) and iterable.get('type') == 'range':
                # Get start value
                start_node = iterable['start']
                if isinstance(start_node, dict):
                    if start_node.get('type') == 'number':
                        start_val = int(start_node['value'])
                    elif start_node.get('type') == 'variable':
                        var_value = self.variables.get(start_node['name'])
                        if var_value is None:
                            raise NameError(f"Variable '{start_node['name']}' is not defined")
                        start_val = int(var_value)
                    else:
                        raise TypeError(f"Invalid range start type: {start_node.get('type')}")
                else:
                    start_val = int(start_node)
                
                # Get end value
                end_node = iterable['end']
                if isinstance(end_node, dict):
                    if end_node.get('type') == 'number':
                        end_val = int(end_node['value'])
                    elif end_node.get('type') == 'variable':
                        var_value = self.variables.get(end_node['name'])
                        if var_value is None:
                            raise NameError(f"Variable '{end_node['name']}' is not defined")
                        end_val = int(var_value)
                    else:
                        raise TypeError(f"Invalid range end type: {end_node.get('type')}")
                else:
                    end_val = int(end_node)
                
                iterable = list(range(start_val, end_val + 1))  # Make range inclusive
                
            elif isinstance(iterable, dict) and iterable.get('type') == 'variable':
                # Handle array variables
                array_name = iterable['name']
                if array_name not in self.variables:
                    raise NameError(f"Variable '{array_name}' is not defined")
                iterable = self.variables[array_name]
                if not isinstance(iterable, list):
                    raise TypeError(f"Variable '{array_name}' is not an array")
            elif not isinstance(iterable, list):
                raise TypeError(f"Can only iterate over arrays and ranges, got {type(iterable)}")
            
            result = None
            old_value = self.variables.get(iterator_name)
            
            try:
                for value in iterable:
                    self.variables[iterator_name] = value
                    for statement in node['body']:
                        result = self.evaluate_node(statement)
            finally:
                if old_value is not None:
                    self.variables[iterator_name] = old_value
                else:
                    del self.variables[iterator_name]
                    
            return result
            
        elif node_type == 'return':
            return node
            
        elif node_type == 'print':
            args = [self.evaluate_node(arg) for arg in node['arguments']]
            print(*args)
            return None
            
        elif node_type == 'range':
            # Return the range node as is, it will be handled in the for loop
            return node
