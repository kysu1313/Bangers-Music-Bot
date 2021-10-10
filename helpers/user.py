from pprint import pprint

class User:
    def __init__(self, 
                user_id, 
                server_id, 
                username=None, 
                bank=None, 
                wallet=None, 
                messages=None, 
                userLevel=None, 
                experience=None, 
                emojiSent=None, 
                reactionsReceived=None, 
                dateUpdated=None):
        self.user_id = user_id
        self.server_id = server_id
        self.username = username
        self.bank = bank
        self.wallet = wallet
        self.messages = messages
        self.userLevel = userLevel
        self.experience = experience
        self.emojiSent = emojiSent
        self.reactionsReceived = reactionsReceived
        self.dateUpdated = dateUpdated

    def print(self):
        pprint(vars(self))