-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
SELECT substr(created_at, 1, 7) AS month, COUNT(*) AS orders
FROM orders GROUP BY month ORDER BY month
