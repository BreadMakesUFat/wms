BEGIN;

DROP TABLE IF EXISTS deliveries;

CREATE TABLE deliveries (
    ID INTEGER PRIMARY KEY,
    BON TEXT, 
    ArticleID TEXT,
    ArticleDescription TEXT,
    Destination TEXT NOT NULL, 
    Recipient INTEGER, 
    Amount INTEGER, 
    Unit TEXT,
    Date TEXT NOT NULL
);

COMMIT;