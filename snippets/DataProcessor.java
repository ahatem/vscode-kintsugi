public final class DataProcessor {

    private static volatile DataProcessor instance;
    private final long creationTimestamp;

    private DataProcessor() {
        if (instance != null) {
            throw new RuntimeException("Use getInstance() method to create");
        }
        this.creationTimestamp = System.currentTimeMillis();
    }

    public static DataProcessor getInstance() {
        if (instance == null) {
            synchronized (DataProcessor.class) {
                if (instance == null) {
                    instance = new DataProcessor();
                }
            }
        }
        return instance;
    }

    @Override
    public String toString() {
        // Example representation of the instance
        return "Processor instance created at: " + creationTimestamp;
    }
}