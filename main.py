from bot import Bot, logging_conf
import logging
import logging.config

logging.config.dictConfig(logging_conf)
log = logging.getLogger()

if __name__ == '__main__':
    log.info("--> Connecting..")

    bot = Bot()
    bot.run()

    log.info("--> That's all, folks!")