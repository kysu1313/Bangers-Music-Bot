


import json


class Saver:
    def __init__(self):
        self.file_name = 'songs.json'

    def save_song(self, user_id, song):
        data = {}
        data[user_id].append(song.link)
        with open(self.file_name, mode='w') as f:
            json.dump(data, f)

    def get_songs(self, user_id):
        with open(self.file_name, mode='w') as f:
            data = json.load(f)
            for p in data:
                if p == user_id:
                    return p["songs"]
