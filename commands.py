from abc import ABC, abstractmethod
from re import sub
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

    @abstractmethod
    async def on_message(self, client, message):
        pass
    
    def on_setup(self):
        pass 

    def post_help(self):
        pass

#custom command
class DiscordCommand(Command):
    def __init__(self, commandText):
        self.member_lookup = {}
        super().__init__(commandText)
    
    async def on_message(self, client, message):
        await self.dump_users(client, message)

    async def dump_users(self, client, message):
        guild = discord.utils.get(client.guilds, name=config('DISCORD_GUILD'))
        count = 0

        for member in guild.members:
            count+=1
            self.member_lookup[member.id] = {'discord_name': member.name,
                                            'twitter_handle': None}
        
        with open('members.json', 'w') as outfile:
            json.dump(self.member_lookup, outfile, sort_keys=True, indent=4)
        
        await message.channel.send(f"{count} users dumped")

class TwitterCommand(Command):
    def __init__(self, commandText):
        self.TWITTER_USER = config('TWITTER_USERNAME')
        self.RESPONSES = {'jay': 'Server god sparks thank u',
        'thomas': 'loves it when it rains at download'
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
        # clean user typed message
        removed_prefix = message.content.split('.')
        print(removed_prefix)
        try:
            subcommand = removed_prefix[1].split(' ', 1)
            print(subcommand)
        except:
            subcommand = message.content.split(' ', 1)
            print(subcommand)

        if len(subcommand) > 1:
            if subcommand[0] == 'tweet':
                await self.send_tweet(message, subcommand[1])
            else:
                await self.send_tweet(message, subcommand[1])
        elif subcommand[0] == 'cleanse':
            await self.cleanse_timeline(message)
        else:
            await message.channel.send(f"That was not a valid command")

    async def send_tweet(self, message, messageContent):
        messageContent = messageContent.replace("@ ", "@")

        #create unique filename
        uid = uuid.uuid4().hex

        #if we have an attachment
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
    
    async def cleanse_timeline(self, message):
        print(message.author)
        count=0
        for tweet in self.api.user_timeline(count=25):
            if tweet.retweet_count == 0 and tweet.favorite_count == 0:
                count+=1
                self.api.destroy_status(tweet.id)
        await message.channel.send(f"We have deleted {count} total tweets with no likes or retweets.")