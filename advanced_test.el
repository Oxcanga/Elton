// String manipulation
var str: string = "  Hello, World!  "
print("Original string: " + str)
print("Uppercase: " + uppercase(str))
print("Lowercase: " + lowercase(str))
print("Trimmed: " + trim(str))
print("Substring(7, 12): " + substring(str, 7, 12))
var parts: array = split(str, ",")
print("Split by comma: " + join(parts, " "))

// Array manipulation
var arr: array = [1, 2, 3, 4, 5]
print("\nOriginal array: " + join(arr, ", "))
push(arr, 6)
print("After push(6): " + join(arr, ", "))
print("Popped value: " + pop(arr))
print("Array length: " + length(arr))
print("Slice(1, 4): " + join(slice(arr, 1, 4), ", "))
print("Reversed: " + join(reverse(arr), ", "))
print("Joined with '-': " + join(arr, "-"))

// Math functions
var nums: array = [10.7, -3.2, 5.1, 8.9]
print("\nNumbers: " + join(nums, ", "))
print("Max: " + max(nums))
print("Min: " + min(nums))
print("Absolute of -3.2: " + abs(-3.2))
print("Round 10.7: " + round(10.7))
print("Round 5.1234 to 2 decimals: " + round(5.1234, 2))

// Combining features
var words: array = split("apple,banana,orange", ",")
print("\nSorted fruits: " + join(reverse(words), ", "))
print("First fruit uppercase: " + uppercase(words[0]))
print("Total characters: " + length(join(words, "")))
