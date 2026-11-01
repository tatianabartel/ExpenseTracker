\timing on

DROP INDEX IF EXISTS idx_cat, idx_cat_date, idx_date_cat;
EXPLAIN ANALYZE SELECT * FROM expenses
WHERE category = 'food' AND date BETWEEN '2026-01-01' AND '2026-03-31';

CREATE INDEX idx_cat ON expenses (category);
ANALYZE expenses;
EXPLAIN ANALYZE SELECT * FROM expenses
WHERE category = 'food' AND date BETWEEN '2026-01-01' AND '2026-03-31';

DROP INDEX idx_cat;
CREATE INDEX idx_cat_date ON expenses (category, date);
ANALYZE expenses;
EXPLAIN ANALYZE SELECT * FROM expenses
WHERE category = 'food' AND date BETWEEN '2026-01-01' AND '2026-03-31';

DROP INDEX idx_cat_date;
CREATE INDEX idx_date_cat ON expenses (date, category);
ANALYZE expenses;
EXPLAIN ANALYZE SELECT * FROM expenses
WHERE category = 'food' AND date BETWEEN '2026-01-01' AND '2026-03-31';

DROP INDEX idx_date_cat;
CREATE INDEX idx_cat_date ON expenses (category, date);
ANALYZE expenses;
EXPLAIN ANALYZE SELECT * FROM expenses WHERE category = 'food';
