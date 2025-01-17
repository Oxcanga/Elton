// Example Elton program demonstrating new features

// String variables and concatenation
var name: string = "Alice";
var greeting: string = "Hello, " + name + "!";
print(greeting);

// Boolean operations
var a: bool = true;
var b: bool = false;
var c: bool = a && b;
var d: bool = a || b;
print("Boolean operations:");
print("a && b = " + (if (c) "true" else "false"));
print("a || b = " + (if (d) "true" else "false"));

// Function that uses if-else
func isEven(num: int) bool {
    if (num % 2 == 0) {
        return true;
    } else {
        return false;
    }
}

// While loop with control flow
var i: int = 1;
while (i <= 5) {
    if (isEven(i)) {
        print(i + " is even");
    } else {
        print(i + " is odd");
    }
    i = i + 1;
}

// Comparison operators
var x: int = 10;
var y: int = 20;

print("\nComparisons:");
print("x = " + x + ", y = " + y);
print("x < y: " + (if (x < y) "true" else "false"));
print("x > y: " + (if (x > y) "true" else "false"));
print("x == y: " + (if (x == y) "true" else "false"));
print("x != y: " + (if (x != y) "true" else "false"));
print("x <= y: " + (if (x <= y) "true" else "false"));
print("x >= y: " + (if (x >= y) "true" else "false"));