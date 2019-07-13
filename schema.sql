DROP TABLE IF EXISTS purchases;

CREATE TABLE purchases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  amount INTEGER NOT NULL,
  currency TEXT NOT NULL,
  description TEXT NOT NULL,
  purchases_date TEXT NOT NULL
);