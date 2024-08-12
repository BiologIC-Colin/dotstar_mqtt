import asyncio
import logging
from dotstar_controller import DotStar, Pixel_Colours

NUM_PIXELS = 120

# Configuring logging
logging.basicConfig(level=logging.DEBUG)

ds_control = DotStar(NUM_PIXELS)

async def star_control():
    while True:
        await ds_control.run()


async def main():
    logging.debug("Console")
    await asyncio.gather(star_control())


if __name__ == '__main__':
    asyncio.run(main())