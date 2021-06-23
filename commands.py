from abc import ABC, abstractmethod
import discord
from decouple import config
import tweepy
import json
import requests
import uuid
import os

#abstract class, anything that has the annotation @abstractmethod must implement into a sub class
class Command(ABC):
    @abstractmethod
    def __init__(self, commandText):
        self.commandText = commandText

    def on_setup(self):
        pass 

    @abstractmethod
    async def on_message(self, client, message):
        pass

#custom command
class HelloWorldCommand(Command):
    def __init__(self, commandText):
        super().__init__(commandText)
    
    async def on_message(self, client, message):
        await message.channel.send("Hello World!")

class TwitterCommand(Command):
    def __init__(self, commandText):
        self.TWITTER_USER = config('TWITTER_USERNAME')
        self.RESPONSES = {'jay': 'Server god sparks thank u',
        'thomas': 'loves it when it rains at download'
        }
        self.username_lookup = {
            'jimmy': 'RGSMostHated',
            'thomas': 'Furneaux_'
        }
        super().__init__(commandText)

    def on_setup(self):
        # Authenticate to Twitter
        self.auth = tweepy.OAuthHandler(config('API_KEY'),config('API_SECRET_KEY'))
        self.auth.set_access_token(config('ACCESS_TOKEN'),config('ACCESS_TOKEN_SECRET'))
        self.api = tweepy.API(self.auth)

        try:
            self.api.verify_credentials()
            print("Twitter Authentication OK")
        except:
            print("Error during authentication")
    
    async def on_message(self, client, message):
        #clean user typed message
        new_status = message.content.split(' ', 2)
        switch = {
            "tweet": await self.send_tweet(message, new_status[2])
        }

        switch.get(new_status[1])


    async def send_tweet(self, message, messageContent):
        messageContent = messageContent.replace("@ ", "@")

        #create unique filename
        uid = uuid.uuid4().hex

        #if we have an attackment
        if len(message.attachments) > 0:
            #get attachment url
            url = message.attachments[0].url
            #get file response from url
            response = requests.get(url, stream=True)
            extension = os.path.splitext(url)[1]
            
            filename = f"{uid}{extension}"

            #write file
            with open(filename, 'wb') as f:
                f.write(response.content)

            media = self.api.media_upload(filename)
            try:
                #update status with media (deprecated but works, use an alternative)
                self.api.update_status(status=messageContent, media_ids=[media.media_id])
            except:
                #delete file
                os.remove(filename)
        else:
            self.api.update_status(status=messageContent)
            await message.channel.send(f"Tweet sent https://twitter.com/{self.TWITTER_USER}/status/{self.api.user_timeline(screen_name=self.TWITTER_USER, count = 1)[0].id}")