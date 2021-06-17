# bot.py

import discord
from decouple import config

TOKEN = config('DISCORD_TOKEN')
GUILD = config('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True

class CustomClient(discord.Client):
    async def on_ready(self):
        guild = discord.utils.get(client.guilds, name=GUILD)
        
        print(f"{client.user} is connected to {guild.name} using id {guild.id}")

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(f"Hi {member.name}, fuck you.")

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content == 'jay':
            await message.channel.send("jay is a cuck")
    

client = CustomClient(intents=intents)
client.run(TOKEN)