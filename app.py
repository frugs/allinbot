import asyncio
import os
import sys
import traceback

import discord
import allinbot


def run_coroutine_handle_error(coro, event_loop):
    async def inner():
        try:
            return await coro
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            event_loop.stop()

    return asyncio.run_coroutine_threadsafe(inner(), event_loop)


def main():
    token = os.getenv("BOT_TOKEN", "")
    twitch_client_id = os.getenv("TWITCH_CLIENT_ID", "")

    if not token:
        raise Exception("Could not resolve bot token")

    event_loop = asyncio.get_event_loop()

    client = discord.Client(loop=event_loop)
    bot = allinbot.Bot(token, client)

    lobster_handler = allinbot.PingRandomPongHandler(
        "!bringoutthedancinglobsters",
        [
            (0.1, "http://i.imgur.com/BMcur.gif"),
            (0.9, "Sorry, they are all asleep right now."),
        ],
    )
    bot.register_handler(lobster_handler)

    bot.register_handler(allinbot.TimeZoneConversionHandler())

    bot.register_handler(allinbot.zerg_mention_handler())
    bot.register_handler(allinbot.protoss_mention_handler())
    bot.register_handler(allinbot.terran_mention_handler())
    bot.register_handler(allinbot.random_mention_handler())

    for handler in allinbot.league_mention_handlers():
        bot.register_handler(handler)

    bot.register_handler(allinbot.Sc2LadderInfoHandler())

    bot.register_handler(allinbot.DynamicPingPongHandler())

    bot.register_handler(allinbot.IsTwitchStreamLiveHandler(twitch_client_id))

    bot.register_handler(allinbot.WinStreakHandler())

    bot.register_handler(allinbot.AppendUtcOffsetHandler())

    bot.register_handler(allinbot.TrialHandler())

    bot.register_handler(allinbot.LadderHeroHandler())

    bot.register_handler(allinbot.FahrenheitToCelsiusHandler())
    bot.register_handler(allinbot.CelsiusToFahrenheitHandler())

    bot.run()


if __name__ == "__main__":
    main()
