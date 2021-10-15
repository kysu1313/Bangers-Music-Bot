


from datetime import datetime
import sqlite3
from sqlite3.dbapi2 import Date


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
                PLAYLIST        INT     NULL,
                USER_ID         TEXT    NOT NULL);''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS PLAYLISTS
                (ID INTEGER PRIMARY KEY NOT NULL,
                NAME                TEXT    NULL,
                CREATED_BY_ID       TEXT    NULL,
                LAST_UPDATED_DATE   TEXT    NULL);''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS PLAYLIST_SONGS
                (ID INTEGER PRIMARY KEY NOT NULL,
                PLAYLIST_ID         INT NOT NULL,
                SONG_ID             INT NOT NULL);''')

        
        self.conn.commit()
        self.conn.close()

    def save_song(self, user, song):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()
        try:
            cursor.execute("""SELECT * FROM SONGS WHERE 
                    (SONG_NAME = '{}' AND URL = '{}' AND USER_ID = '{}' AND PLAYLIST = NULL);""".format(song.name, song.source.url, str(user.id)))
            entry = cursor.fetchone()

            if entry is None:
                cursor.execute("""
                    INSERT INTO SONGS
                    VALUES (NULL, '{}', '{}', NULL, '{}');
            """.format(song.name, song.source.url, str(user.id)))
                    #(SONG_NAME, URL, USER_ID)
                print("song added successfully")
            else:
                print("song already saved")
                self.conn.close()
                return False

            self.conn.commit()
        except Exception as e:
            self.conn.close()
            return e
        self.conn.close()
        return True

    def create_playlist(self, playlist_name, user):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()

        try:
            #cursor.execute("""SELECT * FROM PLAYLISTS WHERE 
            #        (NAME = '{}' AND CREATED_BY_ID = '{}');""".format(playlist_name, str(user.id)))
            #plist = cursor.fetchone()
            entry = self._get_plist(playlist_name, user)

            if entry is None:
                cursor.execute("""
                        INSERT INTO PLAYLISTS
                        VALUES (NULL, '{}', '{}', '{}')
                """.format(playlist_name, str(user.id), str(datetime.now())))

            self.conn.commit()
        except Exception as e:
            self.conn.close()
            return e
        self.conn.close()
        return True

    def add_to_playlist(self, playlist_name, user, song):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()
        try:
            #cursor.execute("""SELECT * FROM PLAYLISTS WHERE 
            #        (NAME = '{}' AND CREATED_BY_ID = '{}');""".format(playlist_name, str(user.id)))
            #plist = cursor.fetchone()
            plist = self._get_plist(playlist_name, user)

            if plist is None:
                return False
            
            cursor.execute("""
                    INSERT INTO SONGS
                    VALUES (NULL, '{}', '{}', '{}');
            """.format(song.name, song.source.url, str(user.id)))
            self.conn.commit()

            #cursor.execute("""SELECT last_insert_rowid() FROM SONGS;""")
            song_id = cursor.lastrowid

            cursor.execute("""
                    INSERT INTO PLAYLIST_SONGS
                    VALUES (NULL, {}, {})
            """.format(plist[0], song_id))
            self.conn.commit()
        except Exception as e:
            self.conn.close()
            return e
        self.conn.close()
        return True

    def _get_plist(self, playlist_name, user):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()
        try:
            cursor.execute("""SELECT * FROM PLAYLISTS WHERE 
                    (NAME = '{}' AND CREATED_BY_ID = '{}');""".format(playlist_name, str(user.id)))
            plist = cursor.fetchone()
            return plist
        except Exception as e:
            pass
        return None

    def get_songs(self, user):
        self.conn = sqlite3.connect(self.file_name)
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    SELECT * FROM SONGS
                    WHERE USER_ID LIKE '{}';
            '''.format(str(user.id)))
            songs = list(cursor.fetchall())
        except Exception as e:
            self.conn.close()
            return e    
        self.conn.close()
        return songs
        
