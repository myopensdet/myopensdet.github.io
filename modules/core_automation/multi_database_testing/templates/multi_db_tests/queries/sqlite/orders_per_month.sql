-- Template from myOpenSDET: https://myopensdet.github.io/
SELECT substr(created_at, 1, 7) AS month, COUNT(*) AS orders
FROM orders GROUP BY month ORDER BY month
