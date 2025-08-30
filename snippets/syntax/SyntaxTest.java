// Sample Java file for testing VSCode theme syntax highlighting
package syntax;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

/**
 * A sample class to demonstrate syntax highlighting.
 * @author YourName
 */
public class SyntaxTest {
    // Constants
    private static final String GREETING = "Hello, World!";
    private static final int MAX_COUNT = 100;

    // Instance variables
    private String name;
    private int count;
    private List<String> items = new ArrayList<>();

    // Enum
    enum Color {
        RED, GREEN, BLUE
    }

    /**
     * Constructor
     * @param name The name to initialize
     */
    public SyntaxTest(String name) {
        this.name = name;
        this.count = 0;
    }

    // Method with various syntax elements
    public void performActions() {
        // Local variables
        int number = 42;
        double pi = 3.14159;
        boolean isActive = true;

        // Control structures
        if (number > 0) {
            System.out.println(GREETING + " " + name);
        } else if (number == 0) {
            System.out.println("Zero detected");
        } else {
            System.out.println("Negative number");
        }

        // Loop
        for (int i = 0; i < MAX_COUNT; i++) {
            items.add("Item " + i);
        }

        // Switch with enum
        Color color = Color.BLUE;
        switch (color) {
            case RED:
                System.out.println("Color is red");
                break;
            case GREEN:
                System.out.println("Color is green");
                break;
            case BLUE:
                System.out.println("Color is blue");
                break;
            default:
                System.out.println("Unknown color");
        }

        // Lambda expression
        Consumer<String> printer = (s) -> System.out.println(s);
        items.forEach(printer);

        // Try-catch
        try {
            int result = 10 / number;
            System.out.println("Result: " + result);
        } catch (ArithmeticException e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            System.out.println("Cleanup complete");
        }

        // Generics and collections
        Map<String, Integer> scores = new HashMap<>();
        scores.put("Alice", 95);
        scores.put("Bob", 85);
    }

    // Getter with annotation
    @Deprecated
    public String getName() {
        return name;
    }

    // Main method
    public static void main(String[] args) {
        SyntaxTest test = new SyntaxTest("TestUser");
        test.performActions();
    }
}