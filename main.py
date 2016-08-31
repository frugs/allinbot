import os
import configparser
import discord
import allinbot

CONFIG_FILE = 'bot.cfg'
BOT_TOKEN_ENVIRONMENT_VARIABLE = 'BOT_TOKEN'


def main():

    if os.path.isfile(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read('bot.cfg')
        try:
            token = config['authentication']['token']
        except configparser.Error:
            print('Failed to parse configuration from ' + CONFIG_FILE)
            raise
    else:
        token = os.environ.get(BOT_TOKEN_ENVIRONMENT_VARIABLE)

    if not token:
        raise Exception("Could not resolve bot token")

    bot = allinbot.Bot(token, discord.Client())

    bot.register_handler(allinbot.logging_handler)
    bot.register_handler(allinbot.create_ping_pong_handler("!test", "test!"))
    bot.register_handler(
        allinbot.create_ping_pong_handler("!winrate", "http://allinwinrateleaderboard.azurewebsites.net/"))
    bot.register_handler(allinbot.choose_map_handler)

    bot.start()
    bot.stop()

if __name__ == '__main__':
    main()

