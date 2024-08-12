import asyncio
import sys
from dataclasses import dataclass
import logging
import spidev

dotStar_start_frame = [0x00, 0x00, 0x00, 0x00]


@dataclass
class DotStar_Pixel:
    a: int  # Brightness
    r: int
    g: int
    b: int

    def get_pixel(self) -> tuple[int, int, int, int]:
        return self.a, self.r, self.g, self.b


Pixel_Colours = {
    "off": DotStar_Pixel(0, 0, 0, 0),
    "blue": DotStar_Pixel(5, 0, 0, 255),
    "red": DotStar_Pixel(5, 255, 0, 0),
    "green": DotStar_Pixel(5, 0, 255, 0),
    "warm white": DotStar_Pixel(2, 239, 235, 216)
}


class DotStar:
    def __init__(self, pixel_count):
        self.pixel_count = pixel_count
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 10000000

        logging.debug("Dotstar initialized")

    def _add_EoF(self, data: list[int]):
        end_count = 8
        for i in range(end_count):
            data.append(0x00)
        return data

    async def set_solid_rgb(self, pixel: DotStar_Pixel):

        # Create an empty payload
        pix_list = []
        for i in range(self.pixel_count):
            pix_list.append(pixel.get_pixel())
        await self._update_strip(pix_list)

    async def fire_laser(self, background: DotStar_Pixel, pulseColour: DotStar_Pixel, shotSize: int, speed: int,
                         direction: int):

        # Needs to run until the shot is off the top
        run_length = self.pixel_count + (shotSize)
        print(f"Run length: {run_length}")
        # Set an Index to the first pixel of the run
        index = 0
        # Speed in steps/second
        delay = 1 / speed

        # Set the first frame so the first pixel of the shot is on pixel 1
        pulse_frame = [pulseColour.get_pixel()]
        frame = pulse_frame + [background.get_pixel() for _ in range(self.pixel_count - 1)]

        while index < run_length:
            if direction >= 0:
                frame = [background.get_pixel()] * index  # pixels before pulse
                frame += [pulseColour.get_pixel()] * shotSize  # pulse
                frame += [background.get_pixel()] * max(0, self.pixel_count - (index + shotSize))  # pixels after pulse
            else:  # If direction is negative, pulse in the opposite direction
                frame = [background.get_pixel()] * max(0, self.pixel_count - (index + shotSize))  # pixels before pulse
                frame += [pulseColour.get_pixel()] * shotSize  # pulse
                frame += [background.get_pixel()] * index  # pixels after pulse

            await self._update_strip(frame)
            index += 1
            await asyncio.sleep(delay)


    async def _update_strip(self, pix_list):
        """
        Method to update LED strip based on colors in pixel_colors list
        """
        data = dotStar_start_frame  # We always start with 4 0x00
        length = len(pix_list)
        for i in range(length):
            brightness, r, g, b = pix_list[i]
            data.append(0b11100000 | brightness)  # Assuming that the brightness should be used with bitwise OR
            data.extend([b, g, r])  # Adding the rgb values into data
        data = self._add_EoF(data)
        self.spi.xfer2(data)
        data.clear()
