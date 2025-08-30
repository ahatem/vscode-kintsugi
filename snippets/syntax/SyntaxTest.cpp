// Sample C++ file for testing VSCode theme syntax highlighting
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <memory>
#include <functional>

#define MAX_COUNT 100
const std::string GREETING = "Hello, C++!";

// Forward declaration
class SyntaxTest;

/**
 * @brief A sample class to demonstrate syntax highlighting
 */
class SyntaxTest {
private:
    std::string name;
    int count;
    std::vector<std::string> items;

public:
    // Constructor
    explicit SyntaxTest(const std::string& name) : name(name), count(0) {}

    // Destructor
    ~SyntaxTest() = default;

    // Template function
    template<typename T>
    T add(T a, T b) {
        return a + b;
    }

    // Method with various syntax elements
    void performActions() {
        // Local variables
        int number = 42;
        double pi = 3.14159;
        bool isActive = true;

        // Pointers and references
        int* ptr = &number;
        std::string& ref = name;

        // Control structures
        if (number > 0) {
            std::cout << GREETING << " " << ref << std::endl;
        } else if (number == 0) {
            std::cout << "Zero detected" << std::endl;
        } else {
            std::cout << "Negative number" << std::endl;
        }

        // Loop
        for (int i = 0; i < MAX_COUNT; ++i) {
            items.push_back("Item " + std::to_string(i));
        }

        // Switch
        enum class Color { Red, Green, Blue };
        Color color = Color::Blue;
        switch (color) {
            case Color::Red:
                std::cout << "Color is red" << std::endl;
                break;
            case Color::Green:
                std::cout << "Color is green" << std::endl;
                break;
            case Color::Blue:
                std::cout << "Color is blue" << std::endl;
                break;
        }

        // Lambda expression
        auto printer = [](const std::string& s) { std::cout << "Lambda: " << s << std::endl; };
        for (const auto& item : items) {
            printer(item);
        }

        // Exception handling
        try {
            if (number == 0) throw std::runtime_error("Division by zero");
            double result = 10.0 / number;
            std::cout << "Result: " << result << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }

        // Smart pointers and collections
        auto shared = std::make_shared<std::string>("Shared");
        std::map<std::string, int> scores;
        scores["Alice"] = 95;
        scores["Bob"] = 85;
    }

    // Inline method
    inline std::string getName() const { return name; }
};

// Operator overloading
std::ostream& operator<<(std::ostream& os, const SyntaxTest& obj) {
    os << "SyntaxTest(name: " << obj.getName() << ")";
    return os;
}

// Template class
template<typename T>
class Container {
    T value;
public:
    explicit Container(T val) : value(val) {}
    T getValue() const { return value; }
};

// Macro
#define LOG(msg) std::cout << "LOG: " << msg << std::endl

// Main function
int main() {
    SyntaxTest test("TestUser");
    test.performActions();
    LOG("Macro test");

    // Template usage
    Container<int> container(42);
    std::cout << "Container value: " << container.getValue() << std::endl;

    // Function pointer
    void (*funcPtr)() = []() { std::cout << "Function pointer called" << std::endl; };
    funcPtr();

    return 0;
}