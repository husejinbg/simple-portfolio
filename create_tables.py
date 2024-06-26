import sqlite3
import config

connection = sqlite3.connect(config.DB_FILE)
cursor = connection.cursor()

# Create assets table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        exchange TEXT NOT NULL
    );
""")

# Create portfolio table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY,
        asset_id INTEGER,
        position REAL,
        average_price REAL,
        currency TEXT,
        last_price REAL,
        FOREIGN KEY(asset_id) REFERENCES assets(id)
    );
""")

# Create snapshots table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY,
        asset_id INTEGER,
        position REAL,
        average_price REAL,
        currency TEXT,
        last_price REAL,
        timestamp TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id)
    );
""")

connection.commit()