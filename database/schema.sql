-- SQLite schema for IEE 305 Term Project (Southwest region: AZ, UT, ID, CA,CO)

CREATE TABLE IF NOT EXISTS parks (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    park_code        TEXT    NOT NULL UNIQUE,
    name             TEXT    NOT NULL,
    state_code       TEXT    NOT NULL,
    entrance_fee     INTEGER NOT NULL DEFAULT 0,
    total_activities INTEGER NOT NULL DEFAULT 0,

    -- Check constraints for rubric
    CHECK (entrance_fee >= 0),
    CHECK (total_activities >= 0),
    CHECK (length(state_code) = 2),
    CHECK (state_code IN ('AZ','UT','ID','CA','CO'))
);

CREATE TABLE IF NOT EXISTS visitor_centers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    park_code   TEXT NOT NULL,
    center_name TEXT NOT NULL,

    FOREIGN KEY (park_code) REFERENCES parks(park_code)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    park_code   TEXT NOT NULL,
    event_title TEXT NOT NULL,
    start_date  DATE NOT NULL,
    end_date    DATE,
    is_free     INTEGER NOT NULL DEFAULT 1,

    CHECK (is_free IN (0, 1)),
    CHECK (end_date IS NULL OR end_date >= start_date),

    FOREIGN KEY (park_code) REFERENCES parks(park_code)
        ON DELETE CASCADE
);

