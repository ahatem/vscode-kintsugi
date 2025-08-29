use std::io;

struct Counter {
    count: i32,
}

impl Counter {
    fn new() -> Self {
        Counter { count: 0 }
    }

    fn inc(&mut self) {
        self.count += 1;
        println!("Count: {}", self.count);
    }

    fn reset(&mut self) {
        self.count = 0;
        println!("Reset to 0");
    }
}

fn main() -> io::Result<()> {
    let mut counter = Counter::new();
    loop {
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        match input.trim() {
            "inc" => counter.inc(),
            "reset" => counter.reset(),
            "exit" => break,
            _ => println!("Use: inc, reset, or exit"),
        }
    }
    Ok(())
}
