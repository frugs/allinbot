import json
import os
import asyncio
import aiohttp
import aiohttp.web
import discord
import allinbot
import traceback
import sys


def run_coroutine_handle_error(coro, event_loop):
    async def inner():
        try:
            return await coro
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            event_loop.stop()

    return asyncio.run_coroutine_threadsafe(inner(), event_loop)


def main():
    token = os.environ.get('BOT_TOKEN')
    firebase_config = json.loads(os.getenv('FIREBASE_CONFIG', '{}'))
    twitch_client_id = os.getenv('TWITCH_CLIENT_ID')

    if not token:
        raise Exception("Could not resolve bot token")

    if not firebase_config:
        raise Exception("Could not resolve firebase config")

    event_loop = asyncio.get_event_loop()

    client = discord.Client(loop=event_loop)
    bot = allinbot.Bot(token, client)

    lobster_handler = allinbot.PingRandomPongHandler(
        "!bringoutthedancinglobsters",
        [(0.1, "http://i.imgur.com/BMcur.gif"),
         (0.9, "Sorry, they are all asleep right now.")])
    bot.register_handler(lobster_handler)

    bot.register_handler(allinbot.TimeZoneConversionHandler())

    db_config = firebase_config
    bot.register_handler(allinbot.zerg_mention_handler(db_config))
    bot.register_handler(allinbot.protoss_mention_handler(db_config))
    bot.register_handler(allinbot.terran_mention_handler(db_config))
    bot.register_handler(allinbot.random_mention_handler(db_config))

    for handler in allinbot.league_mention_handlers(db_config):
        bot.register_handler(handler)

    bot.register_handler(allinbot.Sc2LadderInfoHandler(db_config))

    bot.register_handler(allinbot.QueenInjectEfficiencyHandler())

    bot.register_handler(allinbot.DynamicPingPongHandler(db_config))

    bot.register_handler(
        allinbot.IsTwitchStreamLiveHandler(db_config, twitch_client_id))

    bot.register_handler(allinbot.WinStreakHandler(db_config))

    bot.register_handler(allinbot.AppendUtcOffsetHandler())

    async def general_announce(
            request: aiohttp.web.Request) -> aiohttp.web.Response:
        data = await request.json()

        channel_id = data.get("channel_id", "")
        message = data.get("message", "")

        if channel_id and message:
            bot.schedule_task(
                allinbot.GeneralAnnouncementTask(channel_id, message))

        return aiohttp.web.HTTPOk()

    run_coroutine_handle_error(bot.start(), event_loop)

    app = aiohttp.web.Application()
    app.router.add_post('', general_announce)

    run_coroutine_handle_error(
        event_loop.create_server(
            app.make_handler(), host="localhost", port=40862), event_loop)

    event_loop.run_forever()


if __name__ == '__main__':
    main()
