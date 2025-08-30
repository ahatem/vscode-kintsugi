// Sample Rust file for testing VSCode theme syntax highlighting
use std::collections::HashMap;
use std::fmt::Debug;
use std::sync::Arc;

// Constants
const MAX_COUNT: i32 = 100;
const GREETING: &str = "Hello, Rust!";

/// A sample struct to demonstrate syntax highlighting
#[derive(Debug)]
pub struct SyntaxTest<'a> {
    name: &'a str,
    count: i32,
    items: Vec<String>,
}

// Enum
#[derive(Debug)]
enum Color {
    Red,
    Green,
    Blue(u8),
}

// Trait
trait Printable {
    fn print_info(&self);
}

// Struct implementation
impl<'a> SyntaxTest<'a> {
    /// Creates a new SyntaxTest instance
    pub fn new(name: &'a str) -> Self {
        Self {
            name,
            count: 0,
            items: Vec::new(),
        }
    }

    pub fn perform_actions(&mut self) {
        // Local variables
        let number: i32 = 42;
        let pi: f64 = 3.14159;
        let is_active: bool = true;

        // If let
        if let Some(value) = self.increment_count(number) {
            println!("{} {}: {}", GREETING, self.name, value);
        } else {
            println!("No value returned");
        }

        // Match expression
        let color = Color::Blue(255);
        match color {
            Color::Red => println!("Color is red"),
            Color::Green => println!("Color is green"),
            Color::Blue(intensity) => println!("Color is blue with intensity {}", intensity),
        }

        // Loop
        for i in 0..MAX_COUNT {
            self.items.push(format!("Item {}", i));
        }

        // Closure
        let printer = |s: &str| println!("Closure: {}", s);
        self.items.iter().for_each(printer);

        // Result and error handling
        let result = self.divide(10, number);
        match result {
            Ok(value) => println!("Result: {}", value),
            Err(e) => eprintln!("Error: {}", e),
        }

        // Generics and collections
        let mut scores: HashMap<String, i32> = HashMap::new();
        scores.insert(String::from("Alice"), 95);
        scores.insert(String::from("Bob"), 85);
    }

    fn increment_count(&mut self, value: i32) -> Option<i32> {
        self.count += value;
        Some(self.count)
    }

    fn divide(&self, a: i32, b: i32) -> Result<i32, String> {
        if b == 0 {
            Err(String::from("Division by zero"))
        } else {
            Ok(a / b)
        }
    }
}

// Trait implementation
impl<'a> Printable for SyntaxTest<'a> {
    fn print_info(&self) {
        println!("Name: {}, Count: {}, Items: {:?}", self.name, self.count, self.items);
    }
}

// Macro definition
macro_rules! log {
    ($($arg:tt)*) => {
        println!("LOG: {}", format!($($arg)*));
    };
}

// Async function
async fn async_example() -> Result<(), String> {
    log!("Running async example");
    Ok(())
}

// Main function
fn main() {
    let mut test = SyntaxTest::new("TestUser");
    test.perform_actions();
    test.print_info();

    // Using a macro
    log!("Macro test with value: {}", 42);

    // Smart pointer
    let arc = Arc::new(String::from("Shared"));
    let _cloned = Arc::clone(&arc);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_increment_count() {
        let mut test = SyntaxTest::new("Test");
        assert_eq!(test.increment_count(5), Some(5));
    }
}