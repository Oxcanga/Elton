// Test string interpolation
var name: string = "Alice"
var age: int = 25
print("Hello, ${name}! You are ${age} years old")

// Test array slicing with negative indices
var arr: array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("\nArray slicing:")
print("First 3 elements: " + join(arr[0:3], ", "))
print("Last 3 elements: " + join(arr[-3:], ", "))
print("Elements 2 to -2: " + join(arr[1:-1], ", "))

// Test lambda functions
var double: func = lambda(x: int) {
    return x * 2
}
print("\nDouble of 5: " + double(5))

// Test error handling
print("\nError handling:")
try {
    var x: int = 10
    var y: int = 0
    print("Trying to divide by zero...")
    throw "Cannot divide by zero!"
    print("This won't be printed")
} catch err {
    print("Caught error: " + err)
}

// Test array operations with negative indices
print("\nNegative indexing:")
print("Last element: " + arr[-1])
print("Second to last: " + arr[-2])

// Combine features
func processArray(arr: array) array {
    try {
        return map("double", arr[-3:])
    } catch err {
        print("Error in processArray: " + err)
        return []
    }
}

print("\nProcessed last 3 elements:")
print(join(processArray(arr), ", "))
