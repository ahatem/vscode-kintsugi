// Sample JavaScript file for testing VSCode theme syntax highlighting
import { createServer } from 'http';

// Constants
const MAX_COUNT = 100;
const GREETING = 'Hello, JavaScript!';

// Class
class SyntaxTest {
  #name; // Private field
  #count = 0;
  items = [];

  constructor(name) {
    this.#name = name;
  }

  // Method with various syntax elements
  performActions = async () => {
    // Local variables
    const number = 42;
    const pi = 3.14159;
    const isActive = true;

    // If statement
    if (number > 0) {
      console.log(`${GREETING} ${this.#name}`);
    } else if (number === 0) {
      console.log('Zero detected');
    } else {
      console.log('Negative number');
    }

    // For loop with destructuring
    for (let i = 0; i < MAX_COUNT; i++) {
      this.items.push(`Item ${i}`);
    }

    // Object destructuring
    const { name: userName } = { name: 'Alice', score: 95 };
    console.log(`User: ${userName}`);

    // Switch
    const color = 'blue';
    switch (color) {
      case 'red':
        console.log('Color is red');
        break;
      case 'green':
        console.log('Color is green');
        break;
      case 'blue':
        console.log('Color is blue');
        break;
      default:
        console.log('Unknown color');
    }

    // Arrow function
    const printer = (s) => console.log(`Arrow: ${s}`);
    this.items.forEach(printer);

    // Try-catch with async
    try {
      const result = await this.#divide(10, number);
      console.log(`Result: ${result}`);
    } catch (error) {
      console.error(`Error: ${error.message}`);
    }

    // Map and spread operator
    const scores = new Map([['Alice', 95], ['Bob', 85]]);
    const scoreArray = [...scores.entries()];
    console.log('Scores:', scoreArray);
  };

  // Private method
  #divide = async (a, b) => {
    if (b === 0) throw new Error('Division by zero');
    return a / b;
  };

  // Getter
  get name() {
    return this.#name;
  }
}

// IIFE (Immediately Invoked Function Expression)
(function () {
  console.log('IIFE executed');
})();

// Generator function
function* itemGenerator(maxItems) {
  for (let i = 0; i < maxItems; i++) {
    yield `Generated item ${i}`;
  }
}

// Async function
async function runServer() {
  const server = createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Hello, World!\n');
  });

  server.listen(3000, () => {
    console.log('Server running on port 3000');
  });
}

// Main execution
const main = async () => {
  const test = new SyntaxTest('TestUser');
  await test.performActions();

  // Generator usage
  for (const item of itemGenerator(5)) {
    console.log(item);
  }

  // Template literal with expressions
  console.log(`Sum: ${1 + 2}, Array: ${[1, 2, 3]}`);

  // Optional chaining and nullish coalescing
  const obj = { data: { value: 42 } };
  console.log(obj?.data?.value ?? 'Default');
};

// Execute main
main().catch(console.error);

// Export
export { SyntaxTest };