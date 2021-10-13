


import sqlite3


class Saver:
    def __init__(self):
        self.file_name = 'songs.db'

    def create_tables(self):
        self.conn = sqlite3.connect(self.file_name)
        #self.conn.execute('''CREATE TABLE USERS
        #        (ID INT PRIMARY KEY AUTO INCREMENT NOT NULL,
        #        NAME           TEXT    NOT NULL,
        #        USER_ID         TEXT    NOT NULL,
        #        SERVER_ID       TEXT     NOT NULL);''')
        #print("User table created successfully");
        
        self.conn.execute('''CREATE TABLE SONGS
                (ID INT PRIMARY KEY AUTO INCREMENT NOT NULL,
                SONG_NAME       TEXT    NOT NULL,
                URL             TEXT    NULL,
                USER_ID         TEXT    NOT NULL,
                SERVER_ID       TEXT    NOT NULL);''')
        print("User table created successfully");

        self.conn.close()

    def save_song(self, user, server_id, song):
        self.conn = sqlite3.connect(self.file_name)
        self.conn.execute(f'''
                INSERT OR REPLACE INTO SONGS
                (SONG_NAME, URL, USER_ID, SERVER_ID)
                ({song.name}, {song.link}, {user.id}, {server_id})
        ''')
        print("song added successfully")
        self.conn.close()

    def get_songs(self, user_id):
        self.conn = sqlite3.connect(self.file_name)

        self.conn.close()
        
