import discord
from decouple import config
import tweepy
import json

TOKEN = config('DISCORD_TOKEN')
GUILD = config('DISCORD_GUILD')
RESPONSES = {'jay': 'Server god sparks thank u',
'thomas': 'loves it when it rains at download'
}

intents = discord.Intents.default()
intents.members = True
general_channel = None

# Authenticate to Twitter
auth = tweepy.OAuthHandler(config('API_KEY'),config('API_SECRET_KEY'))
auth.set_access_token(config('ACCESS_TOKEN'),config('ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

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

    # async def on_member_join(self, member):
    #     try:
    #         await member.create_dm()
    #         await member.dm_channel.send(f"Hi {member.name}, fuck you.")
    #     except:
    #         await general_channel.send("Cannot dm this user")

    async def on_message(self, message):
        if message.author == client.user:
            return

        elif message.content.find("tweet") == 0:
            new_status = message.content.split(' ', 1)
            api.update_status(status=new_status[1])
            await message.channel.send(f"Tweet sent https://twitter.com/suisadbvy/status/{api.user_timeline(screen_name='suisadbvy', count = 1)[0].id}")

        elif message.content in RESPONSES.keys():
            await message.channel.send(RESPONSES[message.content])

client = CustomClient(intents=intents)
client.run(TOKEN)

