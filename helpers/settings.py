import os


class Settings:

    _slow_mode = False
    _slow_time = 0

    def __init__(self, is_production=False, is_docker=False):
        self.is_production = is_production
        self.is_docker = is_docker
        self.token = ""
        self.id = ""
        self.members = []
        self.get_bot_id()

    @staticmethod
    def set_slow_mode(enabled=None, time=None):
        if enabled is not None:
            if enabled == "on":
                Settings._slow_mode = True
                Settings._slow_time = 15
            elif enabled == "off":
                Settings._slow_mode = False
        if time is not None:
            Settings._slow_time = time

    def get_is_docker(self):
        return self.is_docker

    def get_bot_id(self):
        self.id = os.environ.get('bot_id')
        return self.id

    def get_is_production(self):
        return self.is_production

    def get_bot_token(self):
        self.token = os.environ.get('discord_token')
        return self.token