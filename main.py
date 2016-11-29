import os
import asyncio
import discord
import growler
import allinbot


def main():
    token = os.environ.get('BOT_TOKEN')
    firebase_config_path = os.environ.get('FIREBASE_CONFIG_PATH')

    if not token:
        raise Exception("Could not resolve bot token")

    if not firebase_config_path:
        raise Exception("Could not resolve firebase config")

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

    bot.register_handler(allinbot.ChooseMapHandler())
    bot.register_handler(allinbot.MapPoolHandler())

    bot.register_handler(allinbot.TimeZoneConversionHandler())

    db_config = allinbot.database.load_db_config(firebase_config_path)
    bot.register_handler(allinbot.zerg_mention_handler(db_config))
    bot.register_handler(allinbot.protoss_mention_handler(db_config))
    bot.register_handler(allinbot.terran_mention_handler(db_config))
    bot.register_handler(allinbot.random_mention_handler(db_config))

    bot.register_handler(allinbot.BattleTagRegistrationHandler(db_config))

    web_app = growler.App('allinbot_controller', loop=event_loop)

    @web_app.get('/trial_reminder')
    def index(req, res):
        bot.schedule_task(allinbot.TrialPeriodReminderTask("233736236379013121", ""))
        res.send_text("Trial reminder scheduled")

    try:
        asyncio.ensure_future(bot.start(), loop=event_loop)
        asyncio.Server = web_app.create_server(port=8081)
        event_loop.run_forever()

        print("event loop finished.")

    except Exception as e:
        print(e)
        raise e

    finally:
        event_loop.run_until_complete(bot.stop())
        event_loop.stop()

if __name__ == '__main__':
    main()
