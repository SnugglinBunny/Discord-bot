import discord
from decouple import config
import json

TOKEN = config('DISCORD_TOKEN')
GUILD = config('DISCORD_GUILD')


intents = discord.Intents.default()
intents.members = True
member_lookup = {}

class CustomClient(discord.Client):
    async def on_ready(self):
        guild = discord.utils.get(client.guilds, name=GUILD)
        
        print(f"{client.user} is connected to {guild.name} using id {guild.id}")

        for member in guild.members:
            member_lookup[member.name] = {'discord_id': member.id,
                                            'twitter_handle': None}
        
        with open('members.json', 'w') as outfile:
            json.dump(member_lookup, outfile, sort_keys=True, indent=4)

        # members = '\n - '.join([member.name for member in guild.members])
        # print(f'Guild Members:\n - {members}')


client = CustomClient(intents=intents)
client.run(TOKEN)

