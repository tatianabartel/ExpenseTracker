\timing on

INSERT INTO expenses (amount, category, date, description)
SELECT
    round((0.01 + random() * 499.99)::numeric, 2),
    (ARRAY['food', 'gym', 'transport', 'rent', 'fun'])[1 + floor(random() * 5)::int],
    date '2023-01-01' + floor(random() * 1400)::int,
    'generated ' || i
FROM generate_series(1, 1000000) AS i;

ANALYZE expenses;

SELECT count(*) FROM expenses;
SELECT category, count(*) FROM expenses GROUP BY category ORDER BY category;
