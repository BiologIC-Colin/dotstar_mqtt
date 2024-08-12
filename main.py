import asyncio
import logging
from dotstar_controller import DotStar, Pixel_Colours

NUM_PIXELS = 120

# Configuring logging
logging.basicConfig(level=logging.DEBUG)

ds_control = DotStar(NUM_PIXELS)


async def main():
    # while (1):
    #     ds_control.set_solid_rgb(red_pix)
    #     print("Red")
    #     time.sleep(5)
    #     ds_control.set_solid_rgb(green_pix)
    #     print("Green")
    #     time.sleep(5)
    #     ds_control.set_solid_rgb(blue_pix)
    #     print("Blue")
    #     time.sleep(5)
    logging.debug("Console")
    await ds_control.set_solid_rgb(Pixel_Colours.get("off"))
    for i in range(5):
        await ds_control.fire_laser(Pixel_Colours.get("off"), Pixel_Colours.get("green"), 3, 20, 1)
        await ds_control.fire_laser(Pixel_Colours.get("off"), Pixel_Colours.get("blue"), 3, 20, -1)
        await ds_control.set_solid_rgb(Pixel_Colours.get("off"))

if __name__ == '__main__':
    asyncio.run(main())