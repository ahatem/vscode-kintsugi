// Sample Go file for testing VSCode theme syntax highlighting
package main

import (
	"fmt"
	"sync"
	"time"
)

// Constants
const (
	MaxCount = 100
	Greeting = "Hello, Go!"
)

// Struct definition
type SyntaxTest struct {
	name  string
	count int
	items []string
}

// Interface
type Printable interface {
	PrintInfo()
}

// Struct method
func (s *SyntaxTest) PrintInfo() {
	fmt.Printf("Name: %s, Count: %d, Items: %v\n", s.name, s.count, s.items)
}

// Function with variadic parameters
func add(numbers ...int) int {
	sum := 0
	for _, num := range numbers {
		sum += num
	}
	return sum
}

// Main function
func main() {
	// Struct initialization
	test := SyntaxTest{
		name:  "TestUser",
		count: 0,
		items: make([]string, 0, MaxCount),
	}

	// Local variables
	number := 42
	pi := 3.14159
	isActive := true

	// If statement
	if number > 0 {
		fmt.Println(Greeting, test.name)
	} else if number == 0 {
		fmt.Println("Zero detected")
	} else {
		fmt.Println("Negative number")
	}

	// For loop
	for i := 0; i < MaxCount; i++ {
		test.items = append(test.items, fmt.Sprintf("Item %d", i))
	}

	// Switch with type assertion
	var value interface{} = "Go"
	switch v := value.(type) {
	case string:
		fmt.Printf("String value: %s\n", v)
	case int:
		fmt.Printf("Integer value: %d\n", v)
	default:
		fmt.Println("Unknown type")
	}

	// Anonymous function (closure)
	printer := func(s string) {
		fmt.Printf("Closure: %s\n", s)
	}
	for _, item := range test.items {
		printer(item)
	}

	// Error handling
	result, err := divide(10, number)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("Result: %d\n", result)
	}

	// Map
	scores := make(map[string]int)
	scores["Alice"] = 95
	scores["Bob"] = 85

	// Goroutine with WaitGroup
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		fmt.Println("Goroutine running")
		time.Sleep(time.Second)
	}()
	wg.Wait()

	// Channel
	ch := make(chan string, 1)
	go func() {
		ch <- "Message from goroutine"
	}()
	fmt.Println(<-ch)

	// Call interface method
	var p Printable = &test
	p.PrintInfo()

	// Defer statement
	defer fmt.Println("Deferred cleanup")
}

// Function with error return
func divide(a, b int) (int, error) {
	if b == 0 {
		return 0, fmt.Errorf("division by zero")
	}
	return a / b, nil
}

// Struct with embedded type
type Config struct {
	SyntaxTest
	enabled bool
}

// Example of init function
func init() {
	fmt.Println("Initializing package")
}