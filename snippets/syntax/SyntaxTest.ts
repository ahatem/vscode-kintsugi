// Sample TypeScript file for testing VSCode theme syntax highlighting
import { useState } from 'react';

// Constants
const MAX_COUNT: number = 100;
const GREETING: string = "Hello, TypeScript!";

// Interface
interface Printable {
  printInfo(): void;
}

// Enum
enum Color {
  Red = 'RED',
  Green = 'GREEN',
  Blue = 'BLUE',
}

// Type alias
type User = {
  id: number;
  name: string;
};

// Class with generics
class SyntaxTest<T extends string> implements Printable {
  private name: T;
  private count: number;
  private items: string[] = [];

  constructor(name: T) {
    this.name = name;
    this.count = 0;
  }

  // Method with various syntax elements
  public performActions = async (): Promise<void> => {
    // Local variables
    const number: number = 42;
    const pi: number = 3.14159;
    const isActive: boolean = true;

    // If statement
    if (number > 0) {
      console.log(`${GREETING} ${this.name}`);
    } else if (number === 0) {
      console.log('Zero detected');
    } else {
      console.log('Negative number');
    }

    // For loop
    for (let i = 0; i < MAX_COUNT; i++) {
      this.items.push(`Item ${i}`);
    }

    // Switch with enum
    const color: Color = Color.Blue;
    switch (color) {
      case Color.Red:
        console.log('Color is red');
        break;
      case Color.Green:
        console.log('Color is green');
        break;
      case Color.Blue:
        console.log('Color is blue');
        break;
      default:
        console.log('Unknown color');
    }

    // Arrow function
    const printer: (s: string) => void = (s) => console.log(`Arrow: ${s}`);
    this.items.forEach(printer);

    // Try-catch with async
    try {
      const result = await this.divide(10, number);
        console.log(`Result: ${result}`);
    } catch (error: unknown) {
      console.error(`Error: ${(error as Error).message}`);
    }

    // Map with type
    const scores: Map<string, number> = new Map([
      ['Alice', 95],
      ['Bob', 85],
    ]);
  };

  // Async method
  private async divide(a: number, b: number): Promise<number> {
    if (b === 0) {
      throw new Error('Division by zero');
    }
    return a / b;
  }

  // Getter
  public getName(): T {
    return this.name;
  }

  // Interface implementation
  public printInfo(): void {
    console.log(`Name: ${this.name}, Count: ${this.count}, Items:`, this.items);
  }
}

// Generic function

function identity<T>(value: T): T {
  return value;
}

// Decorators
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    return originalMethod.apply(this, args);
  };
}

// React component
const MyComponent: React.FC = () => {
  const [count, setCount] = useState<number>(0);

  return (
    `<div>
      <h1>{GREETING}</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>`
  );
};

// Main execution
const main = async (): Promise<void> => {
  const test: SyntaxTest<string> = new SyntaxTest('TestUser');
  await test.performActions();
  test.printInfo();

  // Using generic function
  const num: number = identity<number>(42);
  console.log(`Identity: ${num}`);

  // Type assertion
  const user: User = { id: 1, name: 'Alice' } as User;
  console.log(`User: ${user.name}`);
};

// Execute main
main().catch(console.error);

// Export
export default MyComponent;
export { SyntaxTest, Color, User };