BEGIN;

DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS mappings;
DROP TABLE IF EXISTS articleTranslations;

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
    ArticleDescription TEXT,
    ArticleDescriptionTranslated TEXT, 
    Destination TEXT NOT NULL, 
    Recipient INTEGER, 
    Amount INTEGER, 
    Unit TEXT,
    UnitTranslated TEXT, 
    Date TEXT NOT NULL,
    GovernmentCode TEXT,
    PricePerUnit REAL
);

CREATE TABLE mappings (
    ID INTEGER PRIMARY KEY,
    ArticleID TEXT, 
    FromUnit TEXT, 
    Pieces INTEGER
);

CREATE TABLE articleTranslations (
    ArticleID TEXT PRIMARY KEY,
    ArticleDescription TEXT, 
    GovernmentCode TEXT
);

COMMIT;