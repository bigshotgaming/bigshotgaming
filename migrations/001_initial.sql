-- Big Shot Gaming – initial schema
-- SQLite dialect

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    email           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash   TEXT    NOT NULL,
    first_name      TEXT    NOT NULL DEFAULT '',
    last_name       TEXT    NOT NULL DEFAULT '',
    is_staff        INTEGER NOT NULL DEFAULT 0,
    is_superuser    INTEGER NOT NULL DEFAULT 0,
    is_active       INTEGER NOT NULL DEFAULT 1,
    date_joined     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS venues (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    address  TEXT NOT NULL DEFAULT '',
    city     TEXT NOT NULL DEFAULT '',
    state    TEXT NOT NULL DEFAULT '',
    zipcode  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS events (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT    NOT NULL,
    start_date           TEXT    NOT NULL,
    end_date             TEXT    NOT NULL,
    venue_id             INTEGER REFERENCES venues(id),
    participant_limit    INTEGER NOT NULL DEFAULT 0,
    description          TEXT    NOT NULL DEFAULT '',
    is_active            INTEGER NOT NULL DEFAULT 0,
    registration_enabled INTEGER NOT NULL DEFAULT 0,
    prepay_price         REAL    NOT NULL DEFAULT 0.0,
    atd_price            REAL    NOT NULL DEFAULT 0.0,
    waiver_url           TEXT
);

CREATE TABLE IF NOT EXISTS participants (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    event_id    INTEGER NOT NULL REFERENCES events(id),
    signup_time TEXT    NOT NULL DEFAULT (datetime('now')),
    checked_in  INTEGER NOT NULL DEFAULT 0,
    checkin_time TEXT,
    UNIQUE(user_id, event_id)
);

CREATE TABLE IF NOT EXISTS coupons (
    uuid            TEXT    PRIMARY KEY,
    event_id        INTEGER NOT NULL REFERENCES events(id),
    stripe_transaction TEXT,
    activated       INTEGER NOT NULL DEFAULT 0,
    created_time    TEXT    NOT NULL DEFAULT (datetime('now')),
    activated_time  TEXT,
    notes           TEXT,
    participant_id  INTEGER REFERENCES participants(id)
);

CREATE TABLE IF NOT EXISTS waivers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL REFERENCES participants(id),
    name           TEXT    NOT NULL,
    preferred_name TEXT    NOT NULL DEFAULT '',
    minor          INTEGER NOT NULL DEFAULT 0,
    minor_age      INTEGER,
    signed_on      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS posts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT    NOT NULL,
    body         TEXT    NOT NULL DEFAULT '',
    created_time TEXT    NOT NULL DEFAULT (datetime('now')),
    author_id    INTEGER NOT NULL REFERENCES users(id),
    category     TEXT    NOT NULL DEFAULT 'N'
);

CREATE TABLE IF NOT EXISTS schedule_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    start_time  TEXT    NOT NULL,
    end_time    TEXT    NOT NULL,
    event_id    INTEGER NOT NULL REFERENCES events(id)
);

CREATE TABLE IF NOT EXISTS seatmaps (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id  INTEGER NOT NULL UNIQUE REFERENCES events(id),
    seat_size INTEGER NOT NULL DEFAULT 30
);

CREATE TABLE IF NOT EXISTS seats (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    seatmap_id     INTEGER NOT NULL REFERENCES seatmaps(id),
    x              INTEGER NOT NULL,
    y              INTEGER NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'O',
    participant_id INTEGER REFERENCES participants(id)
);

CREATE TABLE IF NOT EXISTS seat_tables (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    seatmap_id INTEGER NOT NULL REFERENCES seatmaps(id),
    x          INTEGER NOT NULL,
    y          INTEGER NOT NULL,
    w          INTEGER NOT NULL,
    h          INTEGER NOT NULL,
    name       TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS sponsors (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT    NOT NULL,
    contact_name        TEXT    NOT NULL DEFAULT '',
    contact_email       TEXT    NOT NULL DEFAULT '',
    contact_phone       TEXT    NOT NULL DEFAULT '',
    lan_rep_id          INTEGER REFERENCES users(id),
    notes               TEXT    NOT NULL DEFAULT '',
    contact_form_url    TEXT    NOT NULL DEFAULT '',
    banner_url          TEXT    NOT NULL DEFAULT '',
    banner_path         TEXT,
    featured_sponsor    INTEGER NOT NULL DEFAULT 0,
    featured_banner_path TEXT
);

CREATE TABLE IF NOT EXISTS event_sponsors (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sponsor_id INTEGER NOT NULL REFERENCES sponsors(id),
    event_id   INTEGER NOT NULL REFERENCES events(id),
    status     TEXT    NOT NULL DEFAULT 'n',
    UNIQUE(sponsor_id, event_id)
);

CREATE TABLE IF NOT EXISTS prizes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    event_sponsor_id INTEGER NOT NULL REFERENCES event_sponsors(id),
    name             TEXT    NOT NULL,
    description      TEXT    NOT NULL DEFAULT '',
    raffle_prize     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS games (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'P'
);

CREATE TABLE IF NOT EXISTS tournaments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    game_id        INTEGER NOT NULL REFERENCES games(id),
    event_id       INTEGER NOT NULL REFERENCES events(id),
    team_size      INTEGER NOT NULL DEFAULT 1,
    max_teams      INTEGER NOT NULL DEFAULT 16,
    rules          TEXT,
    html_rules     TEXT,
    style          TEXT    NOT NULL DEFAULT 'S',
    slugified_name TEXT    NOT NULL DEFAULT '',
    is_active      INTEGER NOT NULL DEFAULT 1,
    has_started    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS teams (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    password      TEXT    NOT NULL,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
    owner_id      INTEGER NOT NULL REFERENCES participants(id)
);

CREATE TABLE IF NOT EXISTS team_members (
    team_id        INTEGER NOT NULL REFERENCES teams(id),
    participant_id INTEGER NOT NULL REFERENCES participants(id),
    PRIMARY KEY(team_id, participant_id)
);

-- Carpool Tracker (Issue #16)
CREATE TABLE IF NOT EXISTS carpool_offers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id    INTEGER NOT NULL REFERENCES participants(id),
    event_id     INTEGER NOT NULL REFERENCES events(id),
    origin_city  TEXT    NOT NULL,
    origin_state TEXT    NOT NULL,
    total_seats  INTEGER NOT NULL DEFAULT 1,
    notes        TEXT    NOT NULL DEFAULT '',
    contact_email TEXT   NOT NULL DEFAULT '',
    created_time TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS carpool_riders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    rider_id    INTEGER NOT NULL REFERENCES participants(id),
    offer_id    INTEGER NOT NULL REFERENCES carpool_offers(id),
    joined_time TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(rider_id, offer_id)
);
