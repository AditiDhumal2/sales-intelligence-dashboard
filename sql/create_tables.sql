-- =====================================================
-- Superstore Database Schema
-- =====================================================

-- Create main sales table
CREATE TABLE sales (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(50),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(50),
    customer_name VARCHAR(100),
    segment VARCHAR(50),
    country VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    region VARCHAR(50),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    product_name VARCHAR(200),
    sales DECIMAL(10, 2),
    quantity INT,
    discount DECIMAL(5, 2),
    profit DECIMAL(10, 2),
    product_id VARCHAR(50),
    postal_code VARCHAR(20),
    year INT,
    month INT,
    quarter INT,
    year_month VARCHAR(7),
    profit_margin DECIMAL(5, 2),
    shipping_days INT
);

-- Create index for better performance
CREATE INDEX idx_order_date ON sales(order_date);
CREATE INDEX idx_customer_id ON sales(customer_id);
CREATE INDEX idx_category ON sales(category);
CREATE INDEX idx_region ON sales(region);
CREATE INDEX idx_product_id ON sales(product_id);

-- Customer RFM table
CREATE TABLE customer_rfm AS
SELECT 
    customer_id,
    DATEDIFF(CURDATE(), MAX(order_date)) AS recency,
    COUNT(DISTINCT order_id) AS frequency,
    ROUND(SUM(sales), 2) AS monetary,
    CASE 
        WHEN DATEDIFF(CURDATE(), MAX(order_date)) <= 30 THEN 'Active'
        WHEN DATEDIFF(CURDATE(), MAX(order_date)) <= 90 THEN 'Engaged'
        WHEN DATEDIFF(CURDATE(), MAX(order_date)) <= 180 THEN 'At-Risk'
        ELSE 'Lost'
    END AS status
FROM sales
GROUP BY customer_id;