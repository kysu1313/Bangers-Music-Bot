


from datetime import datetime
import sqlite3
from sqlite3.dbapi2 import Date


class PlaylistSaver:
    def __init__(self):
        self.file_name = 'songs.db'
        self.conn = sqlite3.connect(self.file_name)

    def create_tables(self):
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

    def get_all_songs(self, a, b, c):
        #self.conn = sqlite3.connect(self.file_name)
        #cursor = self.conn.cursor()
        #try:
        #    cursor.execute("""
        #                INSERT INTO PLAYLISTS
        #                (ID, NAME, CREATED_BY_ID, LAST_UPDATED_DATE)
        #                VALUES (NULL, ?, ?, ?);
        #        """, (a, b, c,))
        #    self.conn.commit()
        #    return ""
        #except Exception as e:
        #    self.conn.close()
        #    return e
        #self.conn.close()
        return True

    def save_song(self, user, song):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""SELECT * FROM SONGS WHERE 
                    (
                        SONG_NAME = ? AND 
                        URL = ? AND 
                        USER_ID = ? AND 
                        PLAYLIST = NULL);""", (song.name, song.source.url, str(user.id),))
            entry = cursor.fetchone()

            if entry is None:
                cursor.execute("""
                    INSERT INTO SONGS
                    VALUES (NULL, ?, ?, NULL, ?);
            """, (song.name, song.source.url, str(user.id),))
                print("song added successfully")
            else:
                print("song already saved")
                return None

            self.conn.commit()
        except Exception as e:
            self.conn.close()
            return e
        #self.conn.close()
        return True

    def create_playlist(self, playlist_name, user):
        cursor = self.conn.cursor()

        try:
            entry = self._get_plist(playlist_name, user.id)

            if entry is None or len(entry) == 0:
                cursor.execute("""
                        INSERT INTO PLAYLISTS
                        (ID, NAME, CREATED_BY_ID, LAST_UPDATED_DATE)
                        VALUES (NULL, ?, ?, ?);
                """, (str(playlist_name), str(user.id), str(datetime.now()),))
                self.conn.commit()
                return True, ""
        except Exception as e:
            pass
            return None, e
        return False, ""

    def add_to_playlist(self, playlist_name, user, song):
        cursor = self.conn.cursor()
        try:
            plist = self._get_plist(playlist_name, user.id)

            if plist is None:
                self.create_playlist(playlist_name, user)
            
            cursor.execute("""
                    INSERT INTO SONGS
                    (ID, URL, SONG_NAME, PLAYLIST, USER_ID)
                    VALUES (NULL, ?, ?, ?, ?);
            """, (song.name, song.source.url, playlist_name, str(user.id),))
            self.conn.commit()

            song_id = cursor.lastrowid

            cursor.execute("""
                    INSERT INTO PLAYLIST_SONGS
                    (ID, NAME, CREATED_BY_ID, LAST_UPDATED_DATE)
                    VALUES (NULL,  {}, {})
            """.format(plist[0], song_id))
            self.conn.commit()
        except Exception as e:
            return e
        return True

    def _get_plist(self, playlist_name, uid):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""SELECT * FROM SONGS WHERE 
                    PLAYLIST = ? AND USER_ID = ?  
                    COLLATE NOCASE;""", (playlist_name, str(uid),))
            plist = cursor.fetchall()
            return plist
        except Exception as e:
            pass
        return None

    def _get_all_plists(self, user):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""SELECT * FROM PLAYLISTS WHERE 
                    CREATED_BY_ID = ?;""", (str(user.id),))
            plists = cursor.fetchall()
            return plists
        except Exception as e:
            pass
        return None

    def get_songs(self, user):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                    SELECT * FROM SONGS
                    WHERE USER_ID=?;
            ''', (str(user.id),))
            songs = list(cursor.fetchall())
        except Exception as e:
            pass
            return e    
        return songs
        
