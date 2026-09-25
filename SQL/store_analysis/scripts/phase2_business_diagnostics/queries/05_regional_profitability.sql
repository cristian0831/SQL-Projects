-- Profitability by region and state.
-- Business question: which regions/states are net-negative despite the
-- company-wide numbers looking healthy in 01-03?
SELECT g.region, g.state, SUM(oi.sales) AS total_sales, SUM(oi.profit) AS total_profit,
    -- Blended margin (SUM(profit)/SUM(sales)), consistent with segment_margin
    -- in 03_customer_segment_profitability.sql. NOT oi.profit_margin directly --
    -- selecting a non-aggregated column under GROUP BY is legal in SQLite but
    -- returns an arbitrary single row's value per group, not a real aggregate.
    ROUND(SUM(oi.profit) / SUM(oi.sales), 2) AS margin,
    COUNT(DISTINCT oi.order_id) AS order_count
FROM order_items oi
JOIN geography g ON oi.postal_code = g.postal_code
GROUP BY g.region, g.state
ORDER BY total_profit ASC;

