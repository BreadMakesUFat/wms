BEGIN;

DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS mappings;

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

CREATE TABLE deliveries (
    BON TEXT PRIMARY KEY, 
    ArticleID TEXT NOT NULL,
    Destination TEXT NOT NULL, 
    Recipient INTEGER, 
    Amount TEXT, 
    Unit TEXT,
    Date TEXT NOT NULL, 
    Time TEXT NOT NULL
);

COMMIT;