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
        if node is None:
            return None
            
        node_type = node.get('type')
        
        if node_type == 'function_call':
            return self.evaluate_function_call(node)
            
        elif node_type == 'number':
            return node['value']
            
        elif node_type == 'string':
            # Remove quotes from string literals
            value = node['value']
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
            
        elif node_type == 'boolean':
            return node['value']
            
        elif node_type == 'variable':
            if node['name'] not in self.variables:
                raise NameError(f"Variable '{node['name']}' is not defined")
            return self.variables[node['name']]
            
        elif node_type == 'binary_op':
            left = self.evaluate_node(node['left'])
            right = self.evaluate_node(node['right'])
            return self.evaluate_binary_op(node['operator'], left, right)
            
        elif node_type == 'array_literal':
            return [self.evaluate_node(element) for element in node['elements']]
            
        elif node_type == 'array_access':
            array = self.evaluate_node({'type': 'variable', 'name': node['array']})
            index = self.evaluate_node(node['index'])
            if not isinstance(array, list):
                raise TypeError(f"Cannot index non-array type: {type(array)}")
            if not isinstance(index, (int, float)):
                raise TypeError(f"Array index must be a number, got {type(index)}")
            index = int(index)
            if index < 0:
                index = len(array) + index
            if index < 0 or index >= len(array):
                raise IndexError(f"Array index {index} out of bounds")
            return array[index]
            
        elif node_type == 'array_slice':
            array = self.evaluate_node({'type': 'variable', 'name': node['array']})
            start = self.evaluate_node(node['start']) if node['start'] is not None else None
            end = self.evaluate_node(node['end']) if node['end'] is not None else None
            if not isinstance(array, list):
                raise TypeError(f"Cannot slice non-array type: {type(array)}")
            if start is not None and not isinstance(start, (int, float)):
                raise TypeError(f"Slice start must be a number, got {type(start)}")
            if end is not None and not isinstance(end, (int, float)):
                raise TypeError(f"Slice end must be a number, got {type(end)}")
            start = int(start) if start is not None else None
            end = int(end) if end is not None else None
            return array[start:end]
            
        elif node_type == 'lambda_declaration':
            return {'type': 'function', 'params': node['params'], 'body': node['body']}
            
        elif node_type == 'function_declaration':
            self.functions[node['name']] = {
                'params': node['params'],
                'body': node['body'],
                'return_type': node['return_type']
            }
            return None
            
        elif node_type == 'return':
            return {'type': 'return', 'value': node['value']}
            
        elif node_type == 'variable_declaration':
            value = self.evaluate_node(node['value'])
            self.variables[node['name']] = value
            return None
            
        elif node_type == 'if':
            condition = self.evaluate_node(node['condition'])
            if condition:
                return self.evaluate_node(node['then_branch'])
            elif node.get('else_branch'):
                return self.evaluate_node(node['else_branch'])
            return None
            
        elif node_type == 'while':
            while self.evaluate_node(node['condition']):
                self.evaluate_node(node['body'])
            return None
            
        elif node_type == 'for':
            iterator = node['iterator']
            iterable = self.evaluate_node(node['iterable'])
            if not isinstance(iterable, list):
                raise TypeError(f"Cannot iterate over non-array type: {type(iterable)}")
            for value in iterable:
                self.variables[iterator] = value
                self.evaluate_node(node['body'])
            return None
            
        elif node_type == 'range':
            start = self.evaluate_node(node['start'])
            end = self.evaluate_node(node['end'])
            step = self.evaluate_node(node['step']) if node.get('step') else 1
            return list(range(int(start), int(end), int(step)))
            
        elif node_type == 'conditional':
            condition = self.evaluate_node(node['condition'])
            if condition:
                return self.evaluate_node(node['then'])
            elif node['else'] is not None:
                return self.evaluate_node(node['else'])
            else:
                return None
                
        elif node_type == 'try_catch':
            try:
                result = None
                for statement in node['try_body']:
                    result = self.evaluate_node(statement)
            except Exception as e:
                # Store error in catch variable
                old_value = self.variables.get(node['catch_var'])
                self.variables[node['catch_var']] = str(e)
                
                # Execute catch block
                result = None
                for statement in node['catch_body']:
                    result = self.evaluate_node(statement)
                    
                # Restore old value if it existed
                if old_value is not None:
                    self.variables[node['catch_var']] = old_value
                else:
                    del self.variables[node['catch_var']]
                    
            return result
            
        elif node_type == 'throw':
            error_msg = self.evaluate_node(node['value'])
            raise Exception(str(error_msg))
            
        elif node_type == 'var_declaration':
            name = node['name']
            value = self.evaluate_node(node['value'])
            if isinstance(value, str) and value.startswith('_lambda_'):
                # Store lambda function with variable name
                self.functions[name] = self.functions[value]
                del self.functions[value]  # Remove temporary lambda name
                value = name
            self.variables[name] = value
            return value
            
        elif node_type == 'assignment':
            if node['name'] not in self.variables:
                raise NameError(f"Variable '{node['name']}' is not defined")
            value = self.evaluate_node(node['value'])
            self.variables[node['name']] = value
            return value
            
        elif node_type == 'function_call':
            return self.evaluate_function_call(node)
            
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
            
        raise ValueError(f"Unknown node type: {node_type}")
        
    def evaluate_binary_op(self, operator, left, right):
        if operator == '+':
            # Handle string concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        elif operator == '%':
            return left % right
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '<':
            return left < right
        elif operator == '>':
            return left > right
        elif operator == '<=':
            return left <= right
        elif operator == '>=':
            return left >= right
            
    def evaluate_function_call(self, node):
        func_name = node['name']
        args = [self.evaluate_node(arg) for arg in node['arguments']]
        
        if func_name == 'prtoc':
            print(*args)
            return None
        elif func_name == 'upper':
            if len(args) != 1:
                raise TypeError("upper() expects 1 argument: string")
            return str(args[0]).upper()
        elif func_name == 'lower':
            if len(args) != 1:
                raise TypeError("lower() expects 1 argument: string")
            return str(args[0]).lower()
        elif func_name == 'join':
            if len(args) not in [1, 2]:
                raise TypeError("join() expects 1 or 2 arguments: array, [separator]")
            array = args[0]
            if not isinstance(array, list):
                raise TypeError("First argument to join() must be an array")
            separator = args[1] if len(args) == 2 else ""
            return str(separator).join(str(x) for x in array)
        elif func_name == 'map':
            if len(args) != 2:
                raise TypeError("map() expects 2 arguments: function and array")
            func_name = args[0]
            array = args[1]
            if not isinstance(array, list):
                raise TypeError("Second argument to map() must be an array")
            if func_name not in self.functions:
                raise NameError(f"Function '{func_name}' is not defined")
            
            result = []
            old_variables = self.variables.copy()
            for item in array:
                self.variables[self.functions[func_name]['params'][0]['name']] = item
                for statement in self.functions[func_name]['body']:
                    ret = self.evaluate_node(statement)
                    if isinstance(ret, dict) and ret.get('type') == 'return':
                        result.append(self.evaluate_node(ret['value']))
                        break
            self.variables = old_variables
            return result
        elif func_name == 'filter':
            if len(args) != 2:
                raise TypeError("filter() expects 2 arguments: function and array")
            func_name = args[0]
            array = args[1]
            if not isinstance(array, list):
                raise TypeError("Second argument to filter() must be an array")
            if func_name not in self.functions:
                raise NameError(f"Function '{func_name}' is not defined")
            
            result = []
            old_variables = self.variables.copy()
            for item in array:
                self.variables[self.functions[func_name]['params'][0]['name']] = item
                for statement in self.functions[func_name]['body']:
                    ret = self.evaluate_node(statement)
                    if isinstance(ret, dict) and ret.get('type') == 'return':
                        if self.evaluate_node(ret['value']):
                            result.append(item)
                        break
            self.variables = old_variables
            return result
        elif func_name == 'reduce':
            if len(args) != 3:
                raise TypeError("reduce() expects 3 arguments: function, array, and initial value")
            func_name = args[0]
            array = args[1]
            accumulator = args[2]
            if not isinstance(array, list):
                raise TypeError("Second argument to reduce() must be an array")
            if func_name not in self.functions:
                raise NameError(f"Function '{func_name}' is not defined")
            
            old_variables = self.variables.copy()
            for item in array:
                self.variables[self.functions[func_name]['params'][0]['name']] = accumulator
                self.variables[self.functions[func_name]['params'][1]['name']] = item
                for statement in self.functions[func_name]['body']:
                    ret = self.evaluate_node(statement)
                    if isinstance(ret, dict) and ret.get('type') == 'return':
                        accumulator = self.evaluate_node(ret['value'])
                        break
            self.variables = old_variables
            return accumulator
        elif func_name == 'sort':
            if len(args) not in [1, 2]:
                raise TypeError("sort() expects 1 or 2 arguments: array, [reverse]")
            array = args[0]
            reverse = args[1] if len(args) == 2 else False
            if not isinstance(array, list):
                raise TypeError("First argument to sort() must be an array")
            try:
                if all(isinstance(x, (int, float)) for x in array):
                    return sorted(array, reverse=reverse)
                return sorted(array, key=str, reverse=reverse)
            except TypeError:
                raise TypeError("Array elements must be comparable")
        elif func_name == 'unique':
            if len(args) != 1:
                raise TypeError("unique() expects 1 argument: array")
            array = args[0]
            if not isinstance(array, list):
                raise TypeError("Argument to unique() must be an array")
            seen = set()
            result = []
            for item in array:
                item_str = str(item)
                if item_str not in seen:
                    seen.add(item_str)
                    result.append(item)
            return result
        elif func_name == 'listcomp':
            if len(args) != 2:
                raise TypeError("listcomp() expects 2 arguments: function and array")
            func_name = args[0]
            array = args[1]
            if not isinstance(array, list):
                raise TypeError("Second argument to listcomp() must be an array")
            if func_name not in self.functions:
                raise NameError(f"Function '{func_name}' is not defined")
            
            result = []
            old_variables = self.variables.copy()
            for item in array:
                self.variables[self.functions[func_name]['params'][0]['name']] = item
                for statement in self.functions[func_name]['body']:
                    ret = self.evaluate_node(statement)
                    if isinstance(ret, dict) and ret.get('type') == 'return':
                        result.append(self.evaluate_node(ret['value']))
                        break
            self.variables = old_variables
            return result
        elif func_name in self.functions:
            func = self.functions[func_name]
            if len(args) != len(func['params']):
                raise TypeError(f"Function '{func_name}' expects {len(func['params'])} arguments")
            
            old_variables = self.variables.copy()
            for param, arg in zip(func['params'], args):
                self.variables[param['name']] = arg
            
            result = None
            for statement in func['body']:
                result = self.evaluate_node(statement)
                if isinstance(result, dict) and result.get('type') == 'return':
                    result = self.evaluate_node(result['value'])
                    break
            
            self.variables = old_variables
            return result
        else:
            raise NameError(f"Function '{func_name}' is not defined")
