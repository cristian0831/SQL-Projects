-- Profitability by discount band, split by category.
-- Business question: at what discount level does profit start collapsing?
-- Deep discounts (20%+) commonly push profit negative even while sales volume
-- still looks healthy -- this query locates that cliff per category so
-- discount policy can be capped before it erases margin.
WITH banded AS (
    SELECT p.category, 
    CASE
        WHEN oi.discount = 0 THEN '0%'
        WHEN oi.discount <= 0.10 THEN '1-10%'
        WHEN oi.discount <= 0.20 THEN '11-20%'
        WHEN oi.discount <= 0.30 THEN '21-30%'
        WHEN oi.discount <= 0.40 THEN '31-40%'
        WHEN oi.discount < 0.50 THEN '41-49%'
        ELSE '50%+'
    END AS discount_band,
    oi.sales, oi.profit, oi.profit_margin
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
)
SELECT category, discount_band, SUM(sales) AS total_sales, SUM(profit) AS total_profit,
    -- Average of each line item's own margin (unweighted by sale size); read
    -- alongside total_profit above to see both scale and per-item health.
    ROUND(AVG(profit_margin), 3) AS avg_margin
FROM banded
GROUP BY category, discount_band
ORDER BY category,
    CASE discount_band
        WHEN '0%' THEN 1 WHEN '1-10%' THEN 2 WHEN '11-20%' THEN 3
        WHEN '21-30%' THEN 4 WHEN '31-40%' THEN 5 WHEN '41-49%' THEN 6 ELSE 7
    END;
