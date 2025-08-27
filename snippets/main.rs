pub enum Shape {
    Circle(f64),
    Rectangle { width: f64, height: f64 },
}

impl Shape {
    // Calculate the area using pattern matching.
    pub fn area(&self) -> f64 {
        const PI: f64 = 3.1415926535;

        match *self {
            Shape::Circle(radius) => PI * radius * radius,
            Shape::Rectangle { width, height } => width * height,
        }
    }
}

fn main() {
    let my_shape = Shape::Circle(10.0);
    println!("The area is: {:.2}", my_shape.area());
}
