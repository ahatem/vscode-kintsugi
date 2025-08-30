# Sample Python file for testing VSCode theme syntax highlighting
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio

# Constants
MAX_COUNT: int = 100
GREETING: str = "Hello, Python!"

@dataclass
class SyntaxTest:
    """A sample class to demonstrate syntax highlighting."""
    name: str
    count: int = 0
    items: List[str] = None

    def __post_init__(self):
        self.items = []

    def perform_actions(self) -> None:
        # Local variables
        number: int = 42
        pi: float = 3.14159
        is_active: bool = True

        # If statement
        if number > 0:
            print(f"{GREETING} {self.name}")
        elif number == 0:
            print("Zero detected")
        else:
            print("Negative number")

        # List comprehension
        self.items = [f"Item {i}" for i in range(MAX_COUNT)]

        # Match statement (Python 3.10+)
        color = "blue"
        match color:
            case "red":
                print("Color is red")
            case "green":
                print("Color is green")
            case "blue":
                print("Color is blue")
            case _:
                print("Unknown color")

        # Lambda function
        printer = lambda s: print(f"Lambda: {s}")
        for item in self.items:
            printer(item)

        # Exception handling
        try:
            result = 10 / number
            print(f"Result: {result}")
        except ZeroDivisionError as e:
            print(f"Error: {e}")
        finally:
            print("Cleanup complete")

        # Dictionary
        scores: Dict[str, int] = {"Alice": 95, "Bob": 85}

    @staticmethod
    def static_method() -> str:
        return "Static method called"

# Decorator
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_decorator
def divide(a: int, b: int) -> Optional[float]:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

# Async function
async def async_example() -> None:
    print("Starting async task")
    await asyncio.sleep(1)
    print("Async task complete")

# Generator
def item_generator(max_items: int):
    for i in range(max_items):
        yield f"Generated item {i}"

# Main block
if __name__ == "__main__":
    test = SyntaxTest(name="TestUser")
    test.perform_actions()
    print(test.static_method())

    # Async execution
    asyncio.run(async_example())

    # Generator usage
    for item in item_generator(5):
        print(item)

    # F-string with expressions
    print(f"Sum: {1 + 2}, List: {[x for x in range(3)]}")

    # Type hints with complex types
    def process_data(data: List[Dict[str, int]]) -> None:
        print(f"Processing {data}")

    process_data([{"key": 1}, {"key": 2}])

    # Set and tuple
    unique_items = {1, 2, 2, 3}
    coordinates = (10, 20)
    print(f"Set: {unique_items}, Tuple: {coordinates}")