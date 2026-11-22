-- Template from myOpenSDET: https://myopensdet.github.io/
SELECT to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM') AS month, COUNT(*) AS orders
FROM orders GROUP BY month ORDER BY month
