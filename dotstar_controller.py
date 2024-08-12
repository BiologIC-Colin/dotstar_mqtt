import math
import time
import asyncio

import spidev
from dataclasses import dataclass

dotStar_start_frame = [0x00,0x00,0x00,0x00]

@dataclass
class DotStar_Pixel:
    a: int # Brightness
    r: int
    g: int
    b: int

    def get_pixel(self) -> tuple[int, int, int, int]:
        return  self.a, self.r, self.g, self.b

Pixel_Colours = {
    "off" : DotStar_Pixel(0x00,0x00,0x00,0x00),
    "blue" : DotStar_Pixel(5, 0, 0, 255),
    "red" : DotStar_Pixel(5, 255, 0, 0),
    "green" : DotStar_Pixel(5, 0, 255, 0),
    "warm white" : DotStar_Pixel(2, 239, 235, 216)
}
class DotStar:
    def __init__(self, pixel_count):
        self.pixel_count = pixel_count
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 5000000

    def _add_EoF(self, data: list[int]):
        end_count = math.ceil(self.pixel_count/2)
        for i in range(end_count):
            data.append(0x00)
        return data

    async def set_solid_rgb(self, pixel: DotStar_Pixel):

        # Create an empty payload
        pix_list=[]
        for i in range(self.pixel_count):
            pix_list.append(pixel.get_pixel())
        await self._update_strip(pix_list)

    async def fire_laser(self, background: DotStar_Pixel, pulseColour: DotStar_Pixel, ShotSize: int, Speed: int,
                   Direction: int):

        # Set an Index
        index = 1
        # Create the pulse frame
        pulse_frame = [pulseColour.get_pixel() for _ in range(ShotSize)]
        frame = pulse_frame + [background.get_pixel() for _ in range(self.pixel_count - ShotSize)]
        await self._update_strip(frame)






    async def _update_strip(self, pix_list):
        """
        Method to update LED strip based on colors in pixel_colors list
        """
        data = dotStar_start_frame

        for i in range(len(pix_list)):
            myPixel = pix_list[i]
            brightness, r, g, b = pix_list[i]

            data.append(0b11100000 | brightness)  # Assuming that the brightness should be used with bitwise OR
            data.extend([r, g, b])  # Adding the rgb values into data

        self.spi.xfer2(self._add_EoF(data))