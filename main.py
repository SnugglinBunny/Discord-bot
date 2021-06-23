import discord
from decouple import config
import tweepy
import uuid
import os
from commandhandler import CommandHandler


TOKEN = config('DISCORD_TOKEN')
GUILD = config('DISCORD_GUILD')
TWITTER_USER = config('TWITTER_USERNAME')

intents = discord.Intents.default()
intents.members = True
general_channel = None

class CustomClient(discord.Client):
    async def on_ready(self):
        guild = discord.utils.get(client.guilds, name=GUILD)
        self.commandHandler = CommandHandler()
        for command in self.commandHandler.commands:
            command.on_setup()
        
        print(f"{client.user} is connected to {guild.name} using id {guild.id}")

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

    async def on_message(self, message):
        if message.channel.name == config('GENERAL_CHANNEL_NAME'):
            if message.author == client.user or message.author.bot:
                return

            log = open(".log", "a")
            log.write(f"{message.created_at}    {message.author.name}: {message.content}\n")

            command = self.commandHandler.GetCommand(message.content)


            if command is not None:
                self.commandreply = await command.on_message(client, message)
            log.close()



client = CustomClient(intents=intents)
client.run(TOKEN)