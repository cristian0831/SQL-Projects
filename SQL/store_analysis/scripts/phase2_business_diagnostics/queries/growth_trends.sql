--- Yearly sales and profit with Year over Year (YOY)
WITH yearly AS (
    SELECT order_year, SUM(sales) AS total_sales, SUM(profit) AS total_profit,
    COUNT (DISTINCT order_id) AS order_count
    FROM order_items 
    GROUP BY order_year
)
SELECT order_year, total_sales, total_profit, order_count,
ROUND(100.0 * (total_sales - LAG(total_sales) OVER (ORDER BY order_year))
             / LAG(total_sales) OVER (ORDER BY order_year), 1) AS sales_growth_pct
FROM yearly ORDER BY order_year;
