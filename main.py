import asyncio
from dotstar_controller import DotStar, Pixel_Colours

NUM_PIXELS = 120

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
    # ds_control.set_solid_rgb(DotStar_Colours.blue)
    await ds_control.fire_laser(Pixel_Colours.get("blue"), Pixel_Colours.get("red"), 3, 10, 1)
    await ds_control.set_solid_rgb(Pixel_Colours.get("off"))

if __name__ == '__main__':
    asyncio.run(main())