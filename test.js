// test.js - Save this file in your project directory

// Missing semicolon (should be flagged)
const greeting = "Hello, world!"; // Using double quotes instead of single

// Inconsistent indentation (should be flagged)
function calculateSum(a, b) {
  return a + b; // Wrong indentation
}

// Unused variable (should be flagged)
const unusedVariable = 42;

// Console log (might be flagged depending on your config)
console.log(greeting);

// Function call
const result = calculateSum(5, 10);
console.log("The result is: " + result); // Using double quotes again
