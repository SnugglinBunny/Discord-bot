from commands import HelloWorldCommand, TwitterCommand
import commands

class CommandHandler:
    def __init__(self):
        self.commands = [ HelloWorldCommand("hello"), TwitterCommand("twitter") ]

    def GetCommand(self, commandText):
        for command in self.commands:
            if commandText.split(' ', 1)[0].lower() == command.commandText:
                return command
        return None