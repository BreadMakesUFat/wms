BEGIN;

DROP TABLE IF EXISTS deliveries;

CREATE TABLE deliveries (
    ID INTEGER PRIMARY KEY,
    BON TEXT, 
    BODescription TEXT,
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

COMMIT;