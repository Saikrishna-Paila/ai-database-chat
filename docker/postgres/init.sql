-- PostgreSQL Sample Data for AI Database Chat
-- E-commerce sample dataset

-- Create tables
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10, 2),
    shipping_address TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Insert sample customers
INSERT INTO customers (email, first_name, last_name, city, country) VALUES
('john.doe@email.com', 'John', 'Doe', 'New York', 'USA'),
('jane.smith@email.com', 'Jane', 'Smith', 'Los Angeles', 'USA'),
('bob.wilson@email.com', 'Bob', 'Wilson', 'Chicago', 'USA'),
('alice.johnson@email.com', 'Alice', 'Johnson', 'Houston', 'USA'),
('charlie.brown@email.com', 'Charlie', 'Brown', 'Phoenix', 'USA'),
('diana.ross@email.com', 'Diana', 'Ross', 'London', 'UK'),
('edward.jones@email.com', 'Edward', 'Jones', 'Toronto', 'Canada'),
('fiona.green@email.com', 'Fiona', 'Green', 'Sydney', 'Australia'),
('george.harris@email.com', 'George', 'Harris', 'Berlin', 'Germany'),
('helen.white@email.com', 'Helen', 'White', 'Paris', 'France');

-- Insert sample products
INSERT INTO products (name, description, category, price, stock_quantity) VALUES
('Laptop Pro 15', 'High-performance laptop with 15-inch display', 'Electronics', 1299.99, 50),
('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 'Electronics', 29.99, 200),
('Mechanical Keyboard', 'RGB mechanical keyboard with Cherry MX switches', 'Electronics', 149.99, 75),
('USB-C Hub', '7-in-1 USB-C hub with HDMI and SD card reader', 'Electronics', 59.99, 150),
('Monitor 27"', '4K IPS monitor with HDR support', 'Electronics', 449.99, 30),
('Running Shoes', 'Lightweight running shoes for daily training', 'Sports', 89.99, 100),
('Yoga Mat', 'Non-slip yoga mat with carrying strap', 'Sports', 34.99, 200),
('Water Bottle', 'Insulated stainless steel water bottle 32oz', 'Sports', 24.99, 300),
('Fiction Novel', 'Bestselling fiction novel - paperback', 'Books', 14.99, 500),
('Programming Guide', 'Complete guide to modern programming', 'Books', 49.99, 100),
('Coffee Maker', 'Automatic drip coffee maker 12-cup', 'Home', 79.99, 60),
('Desk Lamp', 'LED desk lamp with adjustable brightness', 'Home', 39.99, 120),
('Backpack', 'Water-resistant laptop backpack', 'Accessories', 69.99, 80),
('Headphones', 'Noise-canceling over-ear headphones', 'Electronics', 199.99, 45),
('Smart Watch', 'Fitness tracking smart watch', 'Electronics', 249.99, 55);

-- Insert sample orders
INSERT INTO orders (customer_id, status, total_amount, shipping_address) VALUES
(1, 'completed', 1329.98, '123 Main St, New York, NY 10001'),
(2, 'completed', 299.97, '456 Oak Ave, Los Angeles, CA 90001'),
(3, 'shipped', 149.99, '789 Pine Rd, Chicago, IL 60601'),
(4, 'pending', 539.97, '321 Elm St, Houston, TX 77001'),
(5, 'completed', 89.99, '654 Maple Dr, Phoenix, AZ 85001'),
(1, 'shipped', 449.99, '123 Main St, New York, NY 10001'),
(6, 'completed', 274.97, '10 Downing St, London, UK'),
(7, 'processing', 1549.98, '100 Queen St, Toronto, Canada'),
(8, 'completed', 64.98, '50 George St, Sydney, Australia'),
(9, 'pending', 199.99, '25 Unter den Linden, Berlin, Germany'),
(10, 'completed', 124.98, '8 Champs-Elysees, Paris, France'),
(2, 'shipped', 179.98, '456 Oak Ave, Los Angeles, CA 90001'),
(3, 'completed', 94.98, '789 Pine Rd, Chicago, IL 60601'),
(4, 'completed', 329.98, '321 Elm St, Houston, TX 77001'),
(5, 'processing', 249.99, '654 Maple Dr, Phoenix, AZ 85001');

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
(2, 3, 1, 149.99),
(2, 4, 1, 59.99),
(2, 6, 1, 89.99),
(3, 3, 1, 149.99),
(4, 5, 1, 449.99),
(4, 6, 1, 89.99),
(5, 6, 1, 89.99),
(6, 5, 1, 449.99),
(7, 14, 1, 199.99),
(7, 7, 2, 34.99),
(8, 1, 1, 1299.99),
(8, 15, 1, 249.99),
(9, 9, 2, 14.99),
(9, 7, 1, 34.99),
(10, 14, 1, 199.99),
(11, 11, 1, 79.99),
(11, 12, 1, 39.99),
(12, 3, 1, 149.99),
(12, 2, 1, 29.99),
(13, 8, 2, 24.99),
(13, 7, 1, 34.99),
(14, 13, 1, 69.99),
(14, 15, 1, 249.99),
(15, 15, 1, 249.99);

-- Create indexes for better query performance
CREATE INDEX idx_customers_country ON customers(country);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
