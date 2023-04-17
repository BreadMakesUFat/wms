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
    ID INTEGER PRIMARY KEY,
    BON TEXT, 
    ArticleID TEXT,
    Destination TEXT NOT NULL, 
    Recipient INTEGER, 
    Amount INTEGER, 
    Unit TEXT,
    Date TEXT NOT NULL
);

CREATE TABLE mappings (
    ID INTEGER PRIMARY KEY,
    ArticleID TEXT, 
    FromUnit TEXT, 
    Pieces INTEGER
);

COMMIT;