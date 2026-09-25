-- Sales and profit trend by product category, per year.
-- Business question: which categories are driving (or dragging) the overall
-- Grain: order_year x category.
SELECT oi.order_year, p.category, SUM(oi.sales) AS total_sales, SUM(oi.profit) AS total_profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.order_year, p.category
ORDER BY oi.order_year, p.category;
