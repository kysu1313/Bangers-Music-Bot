#import requests
#import json
#import cryptocompare

#class Apis:
#    def get_joke(self):
#        try:
#            response = requests.get("https://official-joke-api.appspot.com/random_joke") 
#            jid = 0
#            joke_type = ""
#            setup = ""
#            punchline = ""
#            if response is not None:
#                data = json.loads(response.text)
#                jid = data.get("id")
#                joke_type = data.get("type")
#                setup = data.get("setup")
#                punchline = data.get("punchline")
#            return setup, punchline
#        except Exception as e:
#            print("Error: {}".format(e))
#            return None

#    #def get_crypto_price(self, coin):
#    #    curr_coin = cryptocompare.get_price(coin, 'USD')
#    #    curr_price = 0
#    #    if curr_coin is not None:
#    #        curr_price = curr_coin.get(coin)['USD']
#    #    old_price = curr_price
#    #    conn = DbConn()
#    #    exists = conn.get_crypto(coin.upper())
#    #    if exists is None:
#    #        old_coin = conn.insert_crypto(coin, curr_price)
#    #    else:
#    #        old_coin = conn.get_and_update_crypto(coin.upper(), curr_price)
#    #    return old_coin

#    def get_skills(self, name):
#        try:
#            response = requests.get("https://pokeapi.co/api/v2/{}/{}".format("pokemon", name))
#            skills = []
#            abilities = []
#            if response is not None:
#                data = json.loads(response.text)
#                skills = data.get("abilities")
#                for skill in skills:
#                    abilities.append(skill['ability']['name'])
#            return abilities
#        except Exception as e:
#            print("Error: {}".format(e))
#            return None

#    def get_doggo(self):
#        try:
#            response = requests.get("https://api.thedogapi.com/v1/images/search")
#            name = ""
#            url = ""
#            breeds = ""
#            if response is not None:
#                data = json.loads(response.text)
#                try:
#                    breeds = data[0]["breeds"]
#                    name = breeds[0].get("name")
#                except Exception as e:
#                    pass
#                if name == "":
#                    name = "random doggy"
#                url = data[0]["url"]
#            return name, url
#        except Exception as e:
#            print("Error: {}".format(e))
#            return None

#    def get_ascii(self, text, font=None):
#        try:
#            response = None
#            if font is not None:
#                response = requests.get("https://artii.herokuapp.com/make?text={}&font={}".format(text, font))
#            else:
#                response = requests.get("https://artii.herokuapp.com/make?text={}".format(text))
#            result = ""
#            if response is not None:
#                result = response.text
#            return result
#        except Exception as e:
#            print("Error: {}".format(e))
#            return None

#    def get_fonts(self):
#        # https://artii.herokuapp.com/fonts_list
#        try:
#            response = requests.get("https://artii.herokuapp.com/fonts_list")
#            fonts = []
#            if response is not None:
#                data = response.text.split('\n')
#                for font in data:
#                    if "_" not in font:
#                        fonts.append(font)
#            return fonts
#        except Exception as e:
#            print("Error: {}".format(e))
#            return None