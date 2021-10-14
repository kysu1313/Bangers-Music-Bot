


import sqlite3


class PlaylistSaver:
    def __init__(self):
        self.file_name = 'songs.db'

    def create_tables(self):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS SONGS
                (ID INTEGER PRIMARY KEY NOT NULL,
                URL             TEXT    NULL,
                SONG_NAME       TEXT    NOT NULL,
                USER_ID         TEXT    NOT NULL);''')
        print("User table created successfully");
        self.conn.commit()
        self.conn.close()

    def save_song(self, user, song):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()
        cursor.execute("""SELECT * FROM SONGS WHERE 
                (SONG_NAME LIKE '{}' AND URL LIKE '{}' AND USER_ID LIKE '{}')""".format(song.name, song.source.url, str(user.id)))
        entry = cursor.fetchone()

        if entry is None:
            cursor.execute("""
                INSERT INTO SONGS
                VALUES (NULL, '{}', '{}', '{}')
        """.format(song.name, song.source.url, str(user.id)))
                #(SONG_NAME, URL, USER_ID)
            print("song added successfully")
        else:
            print("song already saved")

        self.conn.commit()
        self.conn.close()

    def get_songs(self, user):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()
        cursor.execute('''
                SELECT * FROM SONGS
                WHERE USER_ID LIKE '{}'
        '''.format(str(user.id)))
        songs = list(cursor.fetchall())
        self.conn.close()
        return songs
        
