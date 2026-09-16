--- growth by product category
SELECT oi.order_year, p.category, SUM(oi.sales) AS total_sales, SUM(oi.profit) AS total_profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.order_year, p.category
ORDER BY oi.order_year, p.category;
