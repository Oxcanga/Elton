// Functional programming test

// Map: Double each number
func double(x: int) int {
    return x * 2
}
var numbers: array = [1, 2, 3, 4, 5]
print("Original numbers: " + join(numbers, ", "))
print("Doubled numbers: " + join(map("double", numbers), ", "))

// Filter: Keep only even numbers
func isEven(x: int) bool {
    return x % 2 == 0
}
print("\nEven numbers: " + join(filter("isEven", numbers), ", "))

// Reduce: Sum all numbers
func sum(acc: int, x: int) int {
    return acc + x
}
print("Sum of numbers: " + reduce("sum", numbers, 0))

// Sort and unique
var fruits: array = ["banana", "apple", "orange", "apple", "grape", "banana"]
print("\nOriginal fruits: " + join(fruits, ", "))
print("Sorted fruits: " + join(sort(fruits), ", "))
print("Sorted fruits (reverse): " + join(sort(fruits, true), ", "))
print("Unique fruits: " + join(unique(fruits), ", "))

// Combining features
var mixed: array = [1, 5, 2, 5, 3, 1, 4, 2, 3, 5]
print("\nOriginal mixed: " + join(mixed, ", "))
print("Unique sorted: " + join(sort(unique(mixed)), ", "))

// Map and filter chain
func triple(x: int) int {
    return x * 3
}
func isGreaterThan10(x: int) bool {
    return x > 10
}
print("\nNumbers greater than 10 after tripling: " + 
    join(filter("isGreaterThan10", map("triple", numbers)), ", "))

// Advanced sorting with case conversion
var words: array = ["hello", "WORLD", "Apple", "banana"]
print("\nOriginal words: " + join(words, ", "))

// Convert to lowercase before sorting
func toLower(s: string) string {
    return lowercase(s)
}
print("Sorted case-insensitive: " + join(sort(map("toLower", words)), ", "))

// List comprehension (similar to map but more readable)
func addExclamation(s: string) string {
    return s + "!"
}
print("\nWith exclamation marks: " + join(listcomp("addExclamation", words), ", "))
