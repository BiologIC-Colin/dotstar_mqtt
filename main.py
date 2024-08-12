import asyncio
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from dotstar_controller import DotStar, DCState

NUM_PIXELS = 120


class Logger:
    def __init__(self):
        self.logger = logging.getLogger('DS_Log')
        self.logger.setLevel(logging.DEBUG)
        handler = TimedRotatingFileHandler('ds.log', when="h", interval=12, backupCount=10)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.addHandler(console_handler)
        self.logger.info('Dotstar Program Started')


lg = Logger()
logger = logging.getLogger('DS_Log')


async def star_control(ds_control):
    logger.info("Star Control")
    while True:
        print("ping")
        try:
            await ds_control.run()
        except Exception as e:
            logger.error(f"Error in star_control: {e}")
            break  # or "continue" if we want to keep looping
        await asyncio.sleep(0.1)

async def message_run(ds_control):
    ds_control.state=DCState.OFF


async def star_message(ds_control):
    logger.info("Star Msg Control")
    while True:
        print("ping2")
        try:
            await message_run(ds_control)
        except Exception as e:
            logger.error(f"Error in star_msg_control: {e}")
            break  # or "continue" if we want to keep looping
        await asyncio.sleep(0.1)

async def main():
    logger.info("In Main")

    ds_control = DotStar(NUM_PIXELS)

    await asyncio.gather(star_message(ds_control), star_control(ds_control))


if __name__ == '__main__':
    asyncio.run(main())