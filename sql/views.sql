-- =====================================================
-- Database Views for Business Intelligence
-- =====================================================

-- View: Monthly Performance
CREATE VIEW vw_monthly_performance AS
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margin,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers
FROM sales
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

-- View: Category Performance
CREATE VIEW vw_category_performance AS
SELECT 
    category,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margin,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT product_id) AS products
FROM sales
GROUP BY category
ORDER BY profit DESC;

-- View: Regional Performance
CREATE VIEW vw_regional_performance AS
SELECT 
    region,
    state,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margin,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(DISTINCT order_id) AS orders
FROM sales
GROUP BY region, state
ORDER BY revenue DESC;

-- View: Top Products
CREATE VIEW vw_top_products AS
SELECT 
    product_name,
    category,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margin,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS total_quantity
FROM sales
GROUP BY product_name, category
ORDER BY profit DESC
LIMIT 20;

-- View: Customer Lifetime Value
CREATE VIEW vw_customer_clv AS
SELECT 
    customer_id,
    customer_name,
    segment,
    ROUND(SUM(sales), 2) AS total_spent,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(sales), 2) AS avg_order_value,
    DATEDIFF(CURDATE(), MAX(order_date)) AS days_since_last_order,
    CASE 
        WHEN DATEDIFF(CURDATE(), MAX(order_date)) <= 30 THEN 'Active'
        WHEN DATEDIFF(CURDATE(), MAX(order_date)) <= 90 THEN 'Engaged'
        WHEN DATEDIFF(CURDATE(), MAX(order_date)) <= 180 THEN 'At-Risk'
        ELSE 'Lost'
    END AS customer_status
FROM sales
GROUP BY customer_id, customer_name, segment
ORDER BY total_spent DESC;