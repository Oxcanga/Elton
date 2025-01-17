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
            elif node['name'] == 'abs':
                if len(node['arguments']) != 1:
                    raise TypeError("abs() expects 1 argument: number")
                num = self.evaluate_node(node['arguments'][0])
                if not isinstance(num, (int, float)):
                    raise TypeError("Argument to abs() must be a number")
                return abs(num)
            elif node['name'] == 'max':
                if len(node['arguments']) < 1:
                    raise TypeError("max() expects at least 1 argument")
                args = [self.evaluate_node(arg) for arg in node['arguments']]
                if len(args) == 1 and isinstance(args[0], list):
                    args = args[0]
                if not all(isinstance(x, (int, float)) for x in args):
                    raise TypeError("All arguments to max() must be numbers")
                return max(args)
            elif node['name'] == 'min':
                if len(node['arguments']) < 1:
                    raise TypeError("min() expects at least 1 argument")
                args = [self.evaluate_node(arg) for arg in node['arguments']]
                if len(args) == 1 and isinstance(args[0], list):
                    args = args[0]
                if not all(isinstance(x, (int, float)) for x in args):
                    raise TypeError("All arguments to min() must be numbers")
                return min(args)
            elif node['name'] == 'round':
                if len(node['arguments']) not in [1, 2]:
                    raise TypeError("round() expects 1 or 2 arguments: number, [decimals]")
                num = self.evaluate_node(node['arguments'][0])
                if not isinstance(num, (int, float)):
                    raise TypeError("First argument to round() must be a number")
                if len(node['arguments']) == 2:
                    decimals = int(self.evaluate_node(node['arguments'][1]))
                    return round(num, decimals)
                return float(round(num))
            elif node['name'] == 'push':
                if len(node['arguments']) != 2:
                    raise TypeError("push() expects 2 arguments: array and value")
                array = self.evaluate_node(node['arguments'][0])
                value = self.evaluate_node(node['arguments'][1])
                if not isinstance(array, list):
                    raise TypeError("First argument to push() must be an array")
                array.append(value)
                return len(array)
            elif node['name'] == 'pop':
                if len(node['arguments']) != 1:
                    raise TypeError("pop() expects 1 argument: array")
                array = self.evaluate_node(node['arguments'][0])
                if not isinstance(array, list):
                    raise TypeError("Argument to pop() must be an array")
                if not array:
                    raise IndexError("Cannot pop from empty array")
                return array.pop()
            elif node['name'] == 'length':
                if len(node['arguments']) != 1:
                    raise TypeError("length() expects 1 argument")
                arg = self.evaluate_node(node['arguments'][0])
                if isinstance(arg, list):
                    return float(len(arg))  # Convert to float to match our number type
                elif isinstance(arg, str):
                    return float(len(arg))
                else:
                    raise TypeError("length() argument must be array or string")
            elif node['name'] == 'slice':
                if len(node['arguments']) not in [2, 3]:
                    raise TypeError("slice() expects 2 or 3 arguments: array, start, [end]")
                array = self.evaluate_node(node['arguments'][0])
                start = int(self.evaluate_node(node['arguments'][1]))
                if not isinstance(array, list):
                    raise TypeError("First argument to slice() must be an array")
                if len(node['arguments']) == 3:
                    end = int(self.evaluate_node(node['arguments'][2]))
                    return array[start:end]
                return array[start:]
            elif node['name'] == 'join':
                if len(node['arguments']) not in [1, 2]:
                    raise TypeError("join() expects 1 or 2 arguments: array, [separator]")
                array = self.evaluate_node(node['arguments'][0])
                if not isinstance(array, list):
                    raise TypeError("First argument to join() must be an array")
                if len(node['arguments']) == 2:
                    separator = str(self.evaluate_node(node['arguments'][1]))
                    return separator.join(str(x) for x in array)
                return ''.join(str(x) for x in array)
            elif node['name'] == 'reverse':
                if len(node['arguments']) != 1:
                    raise TypeError("reverse() expects 1 argument: array")
                array = self.evaluate_node(node['arguments'][0])
                if not isinstance(array, list):
                    raise TypeError("Argument to reverse() must be an array")
                return array[::-1]
            elif node['name'] == 'substring':
                if len(node['arguments']) not in [2, 3]:
                    raise TypeError("substring() expects 2 or 3 arguments: string, start, [end]")
                string = str(self.evaluate_node(node['arguments'][0]))
                start = int(self.evaluate_node(node['arguments'][1]))
                if len(node['arguments']) == 3:
                    end = int(self.evaluate_node(node['arguments'][2]))
                    return string[start:end]
                return string[start:]
            elif node['name'] == 'uppercase':
                if len(node['arguments']) != 1:
                    raise TypeError("uppercase() expects 1 argument: string")
                return str(self.evaluate_node(node['arguments'][0])).upper()
            elif node['name'] == 'lowercase':
                if len(node['arguments']) != 1:
                    raise TypeError("lowercase() expects 1 argument: string")
                return str(self.evaluate_node(node['arguments'][0])).lower()
            elif node['name'] == 'trim':
                if len(node['arguments']) != 1:
                    raise TypeError("trim() expects 1 argument: string")
                return str(self.evaluate_node(node['arguments'][0])).strip()
            elif node['name'] == 'split':
                if len(node['arguments']) not in [1, 2]:
                    raise TypeError("split() expects 1 or 2 arguments: string, [delimiter]")
                string = str(self.evaluate_node(node['arguments'][0]))
                if len(node['arguments']) == 2:
                    delimiter = str(self.evaluate_node(node['arguments'][1]))
                    return string.split(delimiter)
                return string.split()
            elif node['name'] == 'map':
                if len(node['arguments']) != 2:
                    raise TypeError("map() expects 2 arguments: function and array")
                func_name = node['arguments'][0]['value']
                array = self.evaluate_node(node['arguments'][1])
                if not isinstance(array, list):
                    raise TypeError("Second argument to map() must be an array")
                if func_name not in self.functions:
                    raise NameError(f"Function '{func_name}' is not defined")
                
                result = []
                for item in array:
                    # Create new scope for function
                    old_variables = self.variables.copy()
                    # Call function with current item
                    self.variables[self.functions[func_name]['params'][0]['name']] = item
                    # Execute function and store result
                    for statement in self.functions[func_name]['body']:
                        ret = self.evaluate_node(statement)
                        if isinstance(ret, dict) and ret.get('type') == 'return':
                            result.append(self.evaluate_node(ret['value']))
                            break
                    # Restore old scope
                    self.variables = old_variables
                return result
                
            elif node['name'] == 'filter':
                if len(node['arguments']) != 2:
                    raise TypeError("filter() expects 2 arguments: function and array")
                func_name = node['arguments'][0]['value']
                array = self.evaluate_node(node['arguments'][1])
                if not isinstance(array, list):
                    raise TypeError("Second argument to filter() must be an array")
                if func_name not in self.functions:
                    raise NameError(f"Function '{func_name}' is not defined")
                
                result = []
                for item in array:
                    # Create new scope for function
                    old_variables = self.variables.copy()
                    # Call function with current item
                    self.variables[self.functions[func_name]['params'][0]['name']] = item
                    # Execute function and check if true
                    for statement in self.functions[func_name]['body']:
                        ret = self.evaluate_node(statement)
                        if isinstance(ret, dict) and ret.get('type') == 'return':
                            if self.evaluate_node(ret['value']):
                                result.append(item)
                            break
                    # Restore old scope
                    self.variables = old_variables
                return result
                
            elif node['name'] == 'reduce':
                if len(node['arguments']) != 3:
                    raise TypeError("reduce() expects 3 arguments: function, array, and initial value")
                func_name = node['arguments'][0]['value']
                array = self.evaluate_node(node['arguments'][1])
                accumulator = self.evaluate_node(node['arguments'][2])
                
                if not isinstance(array, list):
                    raise TypeError("Second argument to reduce() must be an array")
                if func_name not in self.functions:
                    raise NameError(f"Function '{func_name}' is not defined")
                
                for item in array:
                    # Create new scope for function
                    old_variables = self.variables.copy()
                    # Call function with accumulator and current item
                    self.variables[self.functions[func_name]['params'][0]['name']] = accumulator
                    self.variables[self.functions[func_name]['params'][1]['name']] = item
                    # Execute function and update accumulator
                    for statement in self.functions[func_name]['body']:
                        ret = self.evaluate_node(statement)
                        if isinstance(ret, dict) and ret.get('type') == 'return':
                            accumulator = self.evaluate_node(ret['value'])
                            break
                    # Restore old scope
                    self.variables = old_variables
                return accumulator
                
            elif node['name'] == 'sort':
                if len(node['arguments']) not in [1, 2]:
                    raise TypeError("sort() expects 1 or 2 arguments: array, [reverse]")
                array = self.evaluate_node(node['arguments'][0])
                if not isinstance(array, list):
                    raise TypeError("First argument to sort() must be an array")
                reverse = False
                if len(node['arguments']) == 2:
                    reverse = bool(self.evaluate_node(node['arguments'][1]))
                # Convert all elements to same type for comparison
                try:
                    if all(isinstance(x, (int, float)) for x in array):
                        return sorted(array, reverse=reverse)
                    return sorted(array, key=str, reverse=reverse)
                except TypeError:
                    raise TypeError("Array elements must be comparable")
                    
            elif node['name'] == 'unique':
                if len(node['arguments']) != 1:
                    raise TypeError("unique() expects 1 argument: array")
                array = self.evaluate_node(node['arguments'][0])
                if not isinstance(array, list):
                    raise TypeError("Argument to unique() must be an array")
                # Convert to strings for comparison, then back to original type
                seen = set()
                result = []
                for item in array:
                    item_str = str(item)
                    if item_str not in seen:
                        seen.add(item_str)
                        result.append(item)
                return result
                
            elif node['name'] == 'listcomp':
                if len(node['arguments']) != 2:
                    raise TypeError("listcomp() expects 2 arguments: function and array")
                func_name = node['arguments'][0]['value']
                array = self.evaluate_node(node['arguments'][1])
                if not isinstance(array, list):
                    raise TypeError("Second argument to listcomp() must be an array")
                if func_name not in self.functions:
                    raise NameError(f"Function '{func_name}' is not defined")
                
                result = []
                for item in array:
                    # Create new scope for function
                    old_variables = self.variables.copy()
                    # Call function with current item
                    self.variables[self.functions[func_name]['params'][0]['name']] = item
                    # Execute function and store result
                    for statement in self.functions[func_name]['body']:
                        ret = self.evaluate_node(statement)
                        if isinstance(ret, dict) and ret.get('type') == 'return':
                            result.append(self.evaluate_node(ret['value']))
                            break
                    # Restore old scope
                    self.variables = old_variables
                return result
                
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
