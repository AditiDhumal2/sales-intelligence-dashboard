-- =====================================================
-- Superstore Sales Analytics - SQL Queries
-- =====================================================

-- 1. Total Revenue and Profit
SELECT 
    SUM(Sales) AS Total_Revenue,
    SUM(Profit) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Profit_Margin_Percent
FROM superstore;

-- 2. Sales by Category
SELECT 
    Category,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Margin_Percent,
    COUNT(*) AS Order_Count
FROM superstore
GROUP BY Category
ORDER BY Total_Profit DESC;

-- 3. Top 10 Products by Profit
SELECT 
    Product_Name,
    Category,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    COUNT(*) AS Orders
FROM superstore
GROUP BY Product_Name, Category
ORDER BY Total_Profit DESC
LIMIT 10;

-- 4. Monthly Sales Trend
SELECT 
    DATE_FORMAT(`Order Date`, '%Y-%m') AS Month,
    ROUND(SUM(Sales), 2) AS Monthly_Revenue,
    ROUND(SUM(Profit), 2) AS Monthly_Profit,
    COUNT(DISTINCT `Order ID`) AS Orders
FROM superstore
GROUP BY DATE_FORMAT(`Order Date`, '%Y-%m')
ORDER BY Month;

-- 5. Regional Performance
SELECT 
    Region,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Margin_Percent,
    COUNT(DISTINCT `Customer ID`) AS Customers,
    COUNT(DISTINCT `Order ID`) AS Orders
FROM superstore
GROUP BY Region
ORDER BY Total_Sales DESC;

-- 6. Customer Segmentation (RFM Analysis)
WITH RFM AS (
    SELECT 
        `Customer ID`,
        DATEDIFF('2018-12-31', MAX(`Order Date`)) AS Recency,
        COUNT(DISTINCT `Order ID`) AS Frequency,
        ROUND(SUM(Sales), 2) AS Monetary
    FROM superstore
    GROUP BY `Customer ID`
),
RFM_Scores AS (
    SELECT 
        `Customer ID`,
        Recency,
        Frequency,
        Monetary,
        NTILE(4) OVER (ORDER BY Recency DESC) AS R_Score,
        NTILE(4) OVER (ORDER BY Frequency ASC) AS F_Score,
        NTILE(4) OVER (ORDER BY Monetary ASC) AS M_Score
    FROM RFM
)
SELECT 
    `Customer ID`,
    Recency,
    Frequency,
    Monetary,
    CASE 
        WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'VIP Customer'
        WHEN R_Score >= 3 AND F_Score >= 2 THEN 'Loyal Customer'
        WHEN R_Score <= 2 AND F_Score >= 3 THEN 'At-Risk Customer'
        WHEN R_Score <= 2 THEN 'Lost Customer'
        ELSE 'Active Customer'
    END AS Customer_Segment
FROM RFM_Scores
LIMIT 100;

-- 7. Top 5 States by Sales
SELECT 
    State,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Margin_Percent
FROM superstore
GROUP BY State
ORDER BY Total_Sales DESC
LIMIT 5;

-- 8. Sales by Ship Mode
SELECT 
    `Ship Mode`,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    COUNT(*) AS Orders,
    ROUND(AVG(`Shipping_Days`), 1) AS Avg_Shipping_Days
FROM superstore
GROUP BY `Ship Mode`
ORDER BY Total_Sales DESC;

-- 9. Monthly Growth Rate
WITH Monthly_Sales AS (
    SELECT 
        DATE_FORMAT(`Order Date`, '%Y-%m') AS Month,
        ROUND(SUM(Sales), 2) AS Revenue
    FROM superstore
    GROUP BY DATE_FORMAT(`Order Date`, '%Y-%m')
)
SELECT 
    Month,
    Revenue,
    LAG(Revenue) OVER (ORDER BY Month) AS Previous_Month_Revenue,
    ROUND(((Revenue - LAG(Revenue) OVER (ORDER BY Month)) / LAG(Revenue) OVER (ORDER BY Month)) * 100, 2) AS Growth_Percent
FROM Monthly_Sales
ORDER BY Month;

-- 10. Profitable vs Unprofitable Orders
SELECT 
    CASE 
        WHEN Profit > 0 THEN 'Profitable'
        ELSE 'Loss'
    END AS Order_Type,
    COUNT(*) AS Orders,
    ROUND(AVG(Sales), 2) AS Avg_Order_Value,
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM superstore
GROUP BY CASE WHEN Profit > 0 THEN 'Profitable' ELSE 'Loss' END;