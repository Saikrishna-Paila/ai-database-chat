// MongoDB Sample Data for AI Database Chat
// Event logging and analytics sample dataset

// Switch to the database
db = db.getSiblingDB('ai_database_chat');

// Create collections and insert sample data

// Events collection - user activity events
db.events.insertMany([
    {
        event_type: "page_view",
        user_id: "user_001",
        page: "/home",
        timestamp: new Date("2024-01-15T10:30:00Z"),
        session_id: "sess_abc123",
        device: { type: "desktop", browser: "Chrome", os: "Windows" },
        location: { country: "USA", city: "New York" }
    },
    {
        event_type: "page_view",
        user_id: "user_001",
        page: "/products",
        timestamp: new Date("2024-01-15T10:32:00Z"),
        session_id: "sess_abc123",
        device: { type: "desktop", browser: "Chrome", os: "Windows" },
        location: { country: "USA", city: "New York" }
    },
    {
        event_type: "click",
        user_id: "user_001",
        element: "add_to_cart",
        product_id: "prod_laptop",
        timestamp: new Date("2024-01-15T10:35:00Z"),
        session_id: "sess_abc123",
        device: { type: "desktop", browser: "Chrome", os: "Windows" },
        location: { country: "USA", city: "New York" }
    },
    {
        event_type: "purchase",
        user_id: "user_001",
        order_id: "order_001",
        amount: 1299.99,
        timestamp: new Date("2024-01-15T10:40:00Z"),
        session_id: "sess_abc123",
        device: { type: "desktop", browser: "Chrome", os: "Windows" },
        location: { country: "USA", city: "New York" }
    },
    {
        event_type: "page_view",
        user_id: "user_002",
        page: "/home",
        timestamp: new Date("2024-01-15T11:00:00Z"),
        session_id: "sess_def456",
        device: { type: "mobile", browser: "Safari", os: "iOS" },
        location: { country: "UK", city: "London" }
    },
    {
        event_type: "search",
        user_id: "user_002",
        query: "wireless headphones",
        results_count: 15,
        timestamp: new Date("2024-01-15T11:02:00Z"),
        session_id: "sess_def456",
        device: { type: "mobile", browser: "Safari", os: "iOS" },
        location: { country: "UK", city: "London" }
    },
    {
        event_type: "page_view",
        user_id: "user_003",
        page: "/products/electronics",
        timestamp: new Date("2024-01-15T12:00:00Z"),
        session_id: "sess_ghi789",
        device: { type: "tablet", browser: "Chrome", os: "Android" },
        location: { country: "Canada", city: "Toronto" }
    },
    {
        event_type: "click",
        user_id: "user_003",
        element: "product_detail",
        product_id: "prod_monitor",
        timestamp: new Date("2024-01-15T12:05:00Z"),
        session_id: "sess_ghi789",
        device: { type: "tablet", browser: "Chrome", os: "Android" },
        location: { country: "Canada", city: "Toronto" }
    },
    {
        event_type: "signup",
        user_id: "user_004",
        method: "email",
        timestamp: new Date("2024-01-15T14:00:00Z"),
        session_id: "sess_jkl012",
        device: { type: "desktop", browser: "Firefox", os: "macOS" },
        location: { country: "Germany", city: "Berlin" }
    },
    {
        event_type: "purchase",
        user_id: "user_002",
        order_id: "order_002",
        amount: 199.99,
        timestamp: new Date("2024-01-15T11:30:00Z"),
        session_id: "sess_def456",
        device: { type: "mobile", browser: "Safari", os: "iOS" },
        location: { country: "UK", city: "London" }
    },
    {
        event_type: "page_view",
        user_id: "user_005",
        page: "/checkout",
        timestamp: new Date("2024-01-16T09:00:00Z"),
        session_id: "sess_mno345",
        device: { type: "desktop", browser: "Edge", os: "Windows" },
        location: { country: "Australia", city: "Sydney" }
    },
    {
        event_type: "error",
        user_id: "user_005",
        error_code: "PAYMENT_FAILED",
        message: "Card declined",
        timestamp: new Date("2024-01-16T09:05:00Z"),
        session_id: "sess_mno345",
        device: { type: "desktop", browser: "Edge", os: "Windows" },
        location: { country: "Australia", city: "Sydney" }
    }
]);

// Logs collection - application logs
db.logs.insertMany([
    {
        level: "INFO",
        service: "api-gateway",
        message: "Request received",
        endpoint: "/api/products",
        method: "GET",
        response_time_ms: 45,
        status_code: 200,
        timestamp: new Date("2024-01-15T10:30:00Z")
    },
    {
        level: "INFO",
        service: "api-gateway",
        message: "Request received",
        endpoint: "/api/orders",
        method: "POST",
        response_time_ms: 120,
        status_code: 201,
        timestamp: new Date("2024-01-15T10:40:00Z")
    },
    {
        level: "ERROR",
        service: "payment-service",
        message: "Payment processing failed",
        error_code: "INSUFFICIENT_FUNDS",
        transaction_id: "txn_123",
        timestamp: new Date("2024-01-15T11:00:00Z")
    },
    {
        level: "WARNING",
        service: "inventory-service",
        message: "Low stock alert",
        product_id: "prod_laptop",
        current_stock: 5,
        threshold: 10,
        timestamp: new Date("2024-01-15T12:00:00Z")
    },
    {
        level: "INFO",
        service: "api-gateway",
        message: "Request received",
        endpoint: "/api/users",
        method: "GET",
        response_time_ms: 30,
        status_code: 200,
        timestamp: new Date("2024-01-15T14:00:00Z")
    },
    {
        level: "DEBUG",
        service: "auth-service",
        message: "Token validated",
        user_id: "user_001",
        timestamp: new Date("2024-01-15T10:30:01Z")
    },
    {
        level: "ERROR",
        service: "email-service",
        message: "Failed to send email",
        recipient: "user@example.com",
        error: "SMTP connection timeout",
        timestamp: new Date("2024-01-16T08:00:00Z")
    },
    {
        level: "INFO",
        service: "search-service",
        message: "Search query executed",
        query: "wireless headphones",
        results_found: 15,
        response_time_ms: 85,
        timestamp: new Date("2024-01-15T11:02:00Z")
    }
]);

// Metrics collection - system metrics
db.metrics.insertMany([
    {
        metric_name: "cpu_usage",
        service: "api-gateway",
        value: 45.2,
        unit: "percent",
        timestamp: new Date("2024-01-15T10:00:00Z"),
        tags: { environment: "production", region: "us-east-1" }
    },
    {
        metric_name: "memory_usage",
        service: "api-gateway",
        value: 2048,
        unit: "MB",
        timestamp: new Date("2024-01-15T10:00:00Z"),
        tags: { environment: "production", region: "us-east-1" }
    },
    {
        metric_name: "request_count",
        service: "api-gateway",
        value: 1250,
        unit: "requests",
        timestamp: new Date("2024-01-15T10:00:00Z"),
        tags: { environment: "production", region: "us-east-1" }
    },
    {
        metric_name: "cpu_usage",
        service: "api-gateway",
        value: 62.8,
        unit: "percent",
        timestamp: new Date("2024-01-15T11:00:00Z"),
        tags: { environment: "production", region: "us-east-1" }
    },
    {
        metric_name: "memory_usage",
        service: "api-gateway",
        value: 2256,
        unit: "MB",
        timestamp: new Date("2024-01-15T11:00:00Z"),
        tags: { environment: "production", region: "us-east-1" }
    },
    {
        metric_name: "error_rate",
        service: "payment-service",
        value: 2.5,
        unit: "percent",
        timestamp: new Date("2024-01-15T11:00:00Z"),
        tags: { environment: "production", region: "us-east-1" }
    },
    {
        metric_name: "latency_p99",
        service: "search-service",
        value: 150,
        unit: "ms",
        timestamp: new Date("2024-01-15T11:00:00Z"),
        tags: { environment: "production", region: "us-east-1" }
    },
    {
        metric_name: "active_connections",
        service: "database",
        value: 45,
        unit: "connections",
        timestamp: new Date("2024-01-15T11:00:00Z"),
        tags: { environment: "production", region: "us-east-1", db_type: "postgres" }
    }
]);

// Create indexes for better query performance
db.events.createIndex({ "event_type": 1 });
db.events.createIndex({ "user_id": 1 });
db.events.createIndex({ "timestamp": -1 });
db.events.createIndex({ "location.country": 1 });

db.logs.createIndex({ "level": 1 });
db.logs.createIndex({ "service": 1 });
db.logs.createIndex({ "timestamp": -1 });

db.metrics.createIndex({ "metric_name": 1 });
db.metrics.createIndex({ "service": 1 });
db.metrics.createIndex({ "timestamp": -1 });

print("MongoDB initialization complete!");
