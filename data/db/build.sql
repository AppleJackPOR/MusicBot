CREATE TABLE IF NOT EXISTS exp(
    UserID integer PRIMARY KEY,
    XP integer DEFAULT 0,
    Level integet DEFAULT 0,
    XPLock text DEFAULT CURRENT_TIMESTAMP
);