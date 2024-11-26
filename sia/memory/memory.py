import os
import sqlite3


class SiaMemory:

    def __init__(self, character):
        self.db_path = "memory/siamemory.sqlite"
        self.character = character
        if not os.path.exists(self.db_path):
            self.create_database()

    def create_database(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE post (
                id INTEGER PRIMARY KEY,
                character TEXT NOT NULL,
                platform TEXT NOT NULL,
                account TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        connection.commit()
        connection.close()

    def add_post(self, platform, account, content):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO post (character, platform, account, content) VALUES (?, ?, ?, ?)", (self.character, platform, account, content))
        connection.commit()
        connection.close()

    def get_posts(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM post WHERE character=?", (self.character,))
        return cursor.fetchall()
    
    def clear_posts(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM post")
        connection.commit()
        connection.close()
