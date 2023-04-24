BEGIN;

DROP TABLE IF EXISTS stock;

CREATE TABLE stock (
    ArticleID TEXT NOT NULL,
    ArticleDescription TEXT NOT NULL,
    BON TEXT PRIMARY KEY,
    BODescription TEXT,
    BestBefore TEXT,
    Amount INTEGER NOT NULL,
    Location TEXT,
    Weight REAL NOT NULL,
    Unit TEXT NOT NULL,
    Price REAL,
    Date TEXT NOT NULL
);

COMMIT;