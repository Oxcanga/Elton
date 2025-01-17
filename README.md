# Elton Programming Language

Elton is a strictly-typed programming language with clear and unambiguous syntax.

## Features
- Strong typing with explicit type declarations
- Functions with parameters and return values
- String support with escape sequences
- Boolean operations and comparisons
- Control structures (if-else, while loops)
- Basic arithmetic operations
- Comments

## Syntax Overview

```elton
// Variable declaration
var name: type = value;

// Types
- int
- float
- string
- bool

// Function declaration
func functionName(param1: type, param2: type) returnType {
    // function body
}

// Control structures
if (condition) {
    // code
} else {
    // code
}

while (condition) {
    // code
}

// Strings
var message: string = "Hello, World!";
var escaped: string = "Line 1\nLine 2\t\"Quoted\"";

// Boolean operations
var a: bool = true && false;  // AND
var b: bool = true || false;  // OR
var c: bool = !true;         // NOT

// Comparisons
==  // Equal to
!=  // Not equal to
<   // Less than
>   // Greater than
<=  // Less than or equal to
>=  // Greater than or equal to
```

## Examples

### 1. Basic Arithmetic
```elton
func calculateSum(a: int, b: int) int {
    return a + b;
}

var result: int = calculateSum(5, 3);
print(result);  // Output: 8
```

### 2. String Manipulation
```elton
var name: string = "Alice";
print("Hello, " + name + "!");  // Output: Hello, Alice!
```

### 3. Control Flow
```elton
var i: int = 1;
while (i <= 5) {
    if (i % 2 == 0) {
        print(i + " is even");
    } else {
        print(i + " is odd");
    }
    i = i + 1;
}
```

## Running the Interpreter
1. Make sure you have Python 3.8+ installed
2. Run `python elton.py your_program.el`
