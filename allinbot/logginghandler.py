import os
import uuid
import datetime
import json
import discord

from allinbot.handler import Handler


class LoggingHandler(Handler):
    """
    handler which logs everything that is said in all channels to a log file
    """

    def __init__(self, log_dir):
        if not os.path.isdir(log_dir):
            raise ValueError(log_dir + " is not a valid log directory")

        self.log_filename = os.path.join(log_dir, str(uuid.uuid4()) + ".log")

    def can_handle_message(self, message: discord.message):
        return True

    async def handle_message(self, client: discord.client, message: discord.message):
        log = {
            "time_sent": int(datetime.datetime.utcnow().timestamp() * 1000),
            "user": message.author.name + "#" + message.author.discriminator,
            "channel": message.channel.name,
            "message": message.content
        }

        with open(self.log_filename, "a") as log_file:
            log_file.write(json.dumps(log) + "\n")

    def description(self):
        return ""