-- Template from myOpenSDET: https://myopensdet.github.io/
SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(*) AS orders
FROM orders GROUP BY month ORDER BY month
