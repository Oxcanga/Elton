// Test variable declaration with new 'arg' keyword
arg name: string = "Alice"
arg age: int = 25
prtoc("Hello, ${name}! You are ${age} years old")

// Test function declaration with new 'fn' keyword
fn greet(name: string) string {
    return "Hello, " + upper(name) + "!"
}

// Test lambda with new syntax
arg double = lambda(x: int) {
    return x * 2
}

// Test string case functions
arg text: string = "Hello World"
prtoc(lower(text))  // hello world
prtoc(upper(text))  // HELLO WORLD

// Test function calls
prtoc(greet("alice"))  // Hello, ALICE!
prtoc("Double of 5:", double(5))  // Double of 5: 10
