-- customer segment summary
SELECT c.segment, COUNT(DISTINCT oi.order_id) AS order_count, SUM(oi.sales) AS total_sales,
    SUM(oi.profit) AS total_profit, ROUND(SUM(oi.profit) / SUM(oi.sales),2) AS segment_margin,
    ROUND(AVG(oi.profit_margin),2) AS avg_margin
FROM order_items oi JOIN customers c ON oi.customer_id = c.customer_id
GROUP BY c.segment 
ORDER BY total_profit DESC;