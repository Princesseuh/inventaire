import logging
import datetime
import discord

from discord.ext import commands

log = logging.getLogger()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="??", pm_help=True)

        try:
            self.load_extension("inventory")
            log.info("Successfully loaded inventory!")
        except Exception as e:
            log.error('Failed to load inventory. {}: {}'.format(type(e).__name__, e))

    async def on_ready(self):
        log.info("--> READY! Waiting for some cool people to show up..")

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)

    async def on_command(self, ctx):
        log.info(u"{0.content} sent by {0.author.name}".format(ctx.message))

        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await ctx.message.delete()

    async def on_command_error(self, ctx, err):
        log.error(u"{0.content} sent by {0.author.name}. Error : {1}".format(ctx.message, err))

    def get_account(self):
        with open('account') as f:
            return f.read()

    def run(self):
        account = self.get_account()
        super().run(account)


# This is ugly.
logging_conf = {
    "version": 1,
    "formatters": {
        "fmt": {
            "format": u"[%(asctime)s] %(levelname)s %(message)s",
            "datefmt": u"%m/%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "fmt",
            "stream": "ext://sys.stdout"
        },
        "logfile": {
            "class": "logging.FileHandler",
            "formatter": "fmt",
            "filename": "client.log",
            "encoding": "utf-8"
        }
    },
    "root": {
        "handlers": ["console", "logfile"],
        "level": "INFO"
    },
    "loggers": {
        "discord": {
            "level": "CRITICAL"
        }
    },
    "disable_existing_loggers": False
}