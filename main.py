import discord
from decouple import config
import tweepy
import json
import requests
import uuid
import os

TOKEN = config('DISCORD_TOKEN')
GUILD = config('DISCORD_GUILD')
TWITTER_USER = config('TWITTER_USERNAME')
RESPONSES = {'jay': 'Server god sparks thank u',
'thomas': 'loves it when it rains at download',
"love u peepkin": "love u too"}
member_lookup = {}

intents = discord.Intents.default()
intents.members = True
general_channel = None

# Authenticate to Twitter
auth = tweepy.OAuthHandler(config('API_KEY'),config('API_SECRET_KEY'))
auth.set_access_token(config('ACCESS_TOKEN'),config('ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth)

#verify we can access the twitter account
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

#setup discord client class
class CustomClient(discord.Client):
    async def on_ready(self):
        guild = discord.utils.get(client.guilds, name=GUILD)
        for g in guild.channels:
            if g.name == config('GENERAL_CHANNEL_NAME') and str(client.get_channel(g.id).type) == 'text':
                general_channel = client.get_channel(g.id)
                # await general_channel.send("test")
        
        print(f"{client.user} is connected to {guild.name} using id {guild.id}")

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

    async def on_message(self, message):
        if message.channel.name == config('GENERAL_CHANNEL_NAME'):
            if message.author == client.user or message.author.bot:
                return

            log = open(".log", "a")
            log.write(f"{message.created_at}    {message.author.name}: {message.content}\n")

            if message.content.lower().find("tweet") == 0:
                 #clean user typed message
                new_status = message.content.split(' ', 1)
                escaped_status = new_status[1].replace("@ ", "@")

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

                    media = api.media_upload(filename)
                    #update status with media (deprecated but works, use an alternative)
                    try:
                        api.update_status(status=escaped_status, media_ids=[media.media_id])
                    except:
                        os.remove(filename)
                        return
                    #delete file
                    os.remove(filename)
                else:
                    api.update_status(status=escaped_status)
                await message.channel.send(f"Tweet sent https://twitter.com/{TWITTER_USER}/status/{api.user_timeline(screen_name=TWITTER_USER, count = 1)[0].id}")

            #if we don't have an image
            elif message.content in RESPONSES.keys():
                await message.channel.send(RESPONSES[message.content])

            elif message.content == 'twitter.cleanse':
                print(message.author)
                count=0
                for tweet in api.user_timeline(count=100):
                    if tweet.retweet_count == 0 and tweet.favorite_count == 0:
                        count+=1
                        api.destroy_status(tweet.id)
                await message.channel.send(f"We have deleted {count} total tweets with no likes or retweets.")

            elif message.content.lower().find("dump.users") == 0:
                CustomClient.dump_users()
                await message.channel.send(f"Dumped users to file")

            #if the message was not recognized as a command
            else:
                log.write(f" not a valid command")
        log.close()

    def dump_users():
        guild = discord.utils.get(client.guilds, name=GUILD)

        for member in guild.members:
            member_lookup[member.id] = {'discord_name': member.name,
                                            'twitter_handle': None}
        
        with open('members.json', 'w') as outfile:
            json.dump(member_lookup, outfile, sort_keys=True, indent=4)

client = CustomClient(intents=intents)
client.run(TOKEN)