import asyncio
import json
import os
import sys
import traceback

import discord
from google.cloud import datastore

import allinbot


def retrieve_config_value(key: str) -> str:
    datastore_client = datastore.Client()
    return datastore_client.get(datastore_client.key("Config", key))["value"]


def run_coroutine_handle_error(coro, event_loop):
    async def inner():
        try:
            return await coro
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            event_loop.stop()

    return asyncio.run_coroutine_threadsafe(inner(), event_loop)


def main():
    token = os.environ.get("BOT_TOKEN", retrieve_config_value("discordBotToken"))
    firebase_config = json.loads(retrieve_config_value("firebaseConfig"))
    twitch_client_id = retrieve_config_value("twitchClientId")

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

    bot.register_handler(allinbot.DynamicPingPongHandler(db_config))

    bot.register_handler(
        allinbot.IsTwitchStreamLiveHandler(db_config, twitch_client_id))

    bot.register_handler(allinbot.WinStreakHandler(db_config))

    bot.register_handler(allinbot.AppendUtcOffsetHandler())

    bot.run()


if __name__ == '__main__':
    main()
