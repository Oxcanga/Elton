#!/usr/bin/env python3
import sys
from src import Lexer, Parser, Interpreter

def main():
    if len(sys.argv) != 2:
        print("Usage: python elton.py <source_file>")
        sys.exit(1)
        
    try:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
            
        # Create lexer and generate tokens
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse tokens into AST
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Execute the AST
        interpreter = Interpreter()
        interpreter.evaluate(ast)
        
    except FileNotFoundError:
        print(f"Error: Could not find file {sys.argv[1]}")
    except SyntaxError as e:
        print(f"Syntax Error: {str(e)}")
    except Exception as e:
        print(f"Runtime Error: {str(e)}")

if __name__ == "__main__":
    main()
