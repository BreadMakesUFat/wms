BEGIN;

DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS deliveries;

CREATE TABLE stock (
    BON INTEGER PRIMARY KEY,
    ID TEXT NOT NULL,
    Description TEXT NOT NULL,
    Batch TEXT NOT NULL,
    BatchDescription TEXT, 
    BestBefore TEXT,
    Amount INTEGER NOT NULL, 
    Unit TEXT NOT NULL, 
    Weight INTEGER NOT NULL, 
    Price TEXT NOT NULL
);

CREATE TABLE deliveries (
    ID TEXT PRIMARY KEY, 
    BON INTEGER NOT NULL, 
    Description TEXT NOT NULL,
    Amount INTEGER NOT NULL, 
    Destination TEXT NOT NULL, 
    Batch TEXT NOT NULL
    NumberPersons INTEGER NOT NULL
);

COMMIT;