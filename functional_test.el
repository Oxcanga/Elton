// fntional programming test

// Map: Double each number
fn double(x: int) int {
    return x * 2
}
arg numbers: array = [1, 2, 3, 4, 5]
prtoc("Original numbers: " + join(numbers, ", "))
prtoc("Doubled numbers: " + join(map("double", numbers), ", "))

// Filter: Keep only even numbers
fn isEven(x: int) bool {
    return x % 2 == 0
}
prtoc("\nEven numbers: " + join(filter("isEven", numbers), ", "))

// Reduce: Sum all numbers
fn sum(acc: int, x: int) int {
    return acc + x
}
prtoc("Sum of numbers: " + reduce("sum", numbers, 0))

// Sort and unique
arg fruits: array = ["banana", "apple", "orange", "apple", "grape", "banana"]
prtoc("\nOriginal fruits: " + join(fruits, ", "))
prtoc("Sorted fruits: " + join(sort(fruits), ", "))
prtoc("Sorted fruits (reverse): " + join(sort(fruits, true), ", "))
prtoc("Unique fruits: " + join(unique(fruits), ", "))

// Combining features
arg mixed: array = [1, 5, 2, 5, 3, 1, 4, 2, 3, 5]
prtoc("\nOriginal mixed: " + join(mixed, ", "))
prtoc("Unique sorted: " + join(sort(unique(mixed)), ", "))

// Map and filter chain
fn triple(x: int) int {
    return x * 3
}
fn isGreaterThan10(x: int) bool {
    return x > 10
}
prtoc("\nNumbers greater than 10 after tripling: " + 
    join(filter("isGreaterThan10", map("triple", numbers)), ", "))

// Advanced sorting with case conversion
arg words: array = ["hello", "WORLD", "Apple", "banana"]
prtoc("\nOriginal words: " + join(words, ", "))

// Convert to lower before sorting
fn toLower(s: string) string {
    return lower(s)
}
prtoc("Sorted case-insensitive: " + join(sort(map("toLower", words)), ", "))

// List comprehension (similar to map but more readable)
fn addExclamation(s: string) string {
    return s + "!"
}
prtoc("\nWith exclamation marks: " + join(listcomp("addExclamation", words), ", "))
