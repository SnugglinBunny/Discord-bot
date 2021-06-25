from commands import DiscordCommand, TwitterCommand
import commands

class CommandHandler:
    def __init__(self):
        self.commands = [ DiscordCommand("!dump"), TwitterCommand("!tw") ]

    def GetCommand(self, commandText):
        for command in self.commands:
            if commandText[:3].lower() == command.commandText:
                return command
        return None