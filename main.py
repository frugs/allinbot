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

    bot.register_handler(allinbot.LoggingHandler())
    bot.register_handler(allinbot.PingPongHandler("!test", "test!", ""))

    win_rate_handler = allinbot.PingPongHandler(
        "!winrate",
        "http://allinwinrateleaderboard.azurewebsites.net/",
        "!winrate - Links to the All-Inspiration Win Rate Leaderboard")
    bot.register_handler(win_rate_handler)

    bot.register_handler(allinbot.ChooseMapHandler())
    bot.register_handler(allinbot.MapPoolHandler())

    bot.start()
    bot.stop()

if __name__ == '__main__':
    main()

