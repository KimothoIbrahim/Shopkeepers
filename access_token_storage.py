import sqlite3

class TokenStorage:
    def __init__(self):
        self.conn = sqlite3.connect("tokens.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tokens (type TEXT PRIMARY KEY, token TEXT)"
        )
        self.conn.commit()

    def store_token(self, token_type, token_value):
        self.cursor.execute(
            "REPLACE INTO tokens (type, token) VALUES (?, ?)",
            (token_type, token_value),
        )
        self.conn.commit()

    def retrieve_token(self, token_type):
        self.cursor.execute(
            "SELECT token FROM tokens WHERE type = ?", (token_type,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def delete(self):
        self.cursor.execute(
            "DROP TABLE IF EXISTS tokens;"
        )
        self.__init__()

    def close(self):
        self.conn.close()
