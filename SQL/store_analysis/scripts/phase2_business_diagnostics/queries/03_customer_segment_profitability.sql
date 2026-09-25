-- Profitability summary by customer segment (Consumer / Corporate / Home Office).
-- Business question: which segments generate the most profit, and how
-- efficiently (margin) rather than just by volume (sales)?
-- segment_margin = blended margin: SUM(profit)/SUM(sales), weighted by order size.
-- avg_margin     = average of each line item's own profit_margin, unweighted.
-- The two diverge when a segment's profit is concentrated in a few large orders.
SELECT c.segment, COUNT(DISTINCT oi.order_id) AS order_count, SUM(oi.sales) AS total_sales,
    SUM(oi.profit) AS total_profit, ROUND(SUM(oi.profit) / SUM(oi.sales),2) AS segment_margin,
    ROUND(AVG(oi.profit_margin),2) AS avg_margin
FROM order_items oi JOIN customers c ON oi.customer_id = c.customer_id
GROUP BY c.segment 
ORDER BY total_profit DESC;