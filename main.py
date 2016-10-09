import os
import configparser
import asyncio
import discord
import allinbot
import allinbot.logginghandler

CONFIG_FILE = 'bot.cfg'
BOT_TOKEN_ENVIRONMENT_VARIABLE = 'BOT_TOKEN'
LOG_DIR_ENVIRONMENT_VARIABLE = 'LOG_DIR'


def main():

    if os.path.isfile(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read('bot.cfg')
        try:
            token = config['authentication']['token']
            log_dir = config['logging']['log_directory']
        except configparser.Error:
            print('Failed to parse configuration from ' + CONFIG_FILE)
            raise
    else:
        token = os.environ.get(BOT_TOKEN_ENVIRONMENT_VARIABLE)
        log_dir = os.environ.get(LOG_DIR_ENVIRONMENT_VARIABLE)

    if not token:
        raise Exception("Could not resolve bot token")

    event_loop = asyncio.get_event_loop()

    client = discord.Client(loop=event_loop)
    bot = allinbot.Bot(token, client)

    bot.register_handler(allinbot.PingPongHandler("!test", "test!", ""))
    bot.register_handler(allinbot.PingPongHandler("!whoisthebestontheteam", "<@!93018397935144960>"))

    lobster_handler = allinbot.PingRandomPongHandler(
        "!bringoutthedancinglobsters",
        [
            (0.1, "http://i.imgur.com/BMcur.gif"),
            (0.9, "Sorry, they are all asleep right now.")
        ])
    bot.register_handler(lobster_handler)

    win_rate_handler = allinbot.PingPongHandler(
        "!winrate",
        "http://allinwinrateleaderboard.azurewebsites.net/",
        "!winrate - Links to the All-Inspiration Win Rate Leaderboard")
    bot.register_handler(win_rate_handler)

    bot.register_handler(allinbot.ChooseMapHandler())
    bot.register_handler(allinbot.MapPoolHandler())

    bot.register_handler(allinbot.TimeZoneConversionHandler())

    bot.register_handler(allinbot.LoggingHandler(log_dir))

    tasks = [
        allinbot.TrialPeriodReminderTask(client, "233736236379013121", "<@&176016120275402752>")
    ]

    task_scheduler = allinbot.TaskScheduler(event_loop, tasks, 39600)

    try:
        futures = [task_scheduler.start(), bot.start()]
        event_loop.run_until_complete(asyncio.gather(*futures))

    finally:
        event_loop.stop()
        client.close()

if __name__ == '__main__':
    main()
