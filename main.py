import os
import configparser
import discord
import allinbot

CONFIG_FILE = 'bot.cfg'


def main():
    config = configparser.ConfigParser()
    
    if not os.path.isfile(CONFIG_FILE):
        raise FileNotFoundError('Could not find config file ' + CONFIG_FILE)

    config.read('bot.cfg')
    try:
        token = config['authentication']['token']
    except configparser.Error:
        print('Failed to parse configuration from ' + CONFIG_FILE)
        raise

    bot = allinbot.Bot(token, discord.Client())
    bot.register_handler(allinbot.logging_handler)
    bot.register_handler(allinbot.test_handler)

    bot.start()
    bot.stop()

if __name__ == '__main__':
    main()

