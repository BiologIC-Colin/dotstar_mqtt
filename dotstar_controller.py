import asyncio
import colorsys
import sys
import time
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

class DCState:
    INIT = 0
    OFF = 1
    ON = 2


class DotStar:
    def __init__(self, pixel_count):
        self.pixel_count = pixel_count
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 10000000
        self.state = DCState.OFF
        self.last_state = DCState.INIT
        self.diag = 0
        self.rainbow = False

        logging.debug("Dotstar initialized")

    def _add_EoF(self, data: list[int]):
        end_count = 8
        for i in range(end_count):
            data.append(0x00)
        return data

    def _hsl_to_rgb(self, h, s, l):
        return [int(c * 255) for c in colorsys.hls_to_rgb(h, l, s)]

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

    async def set_static_rainbow(self):
        pix_list = []
        brightness = 10

        # Loop over all pixels
        for i in range(self.pixel_count):
            # Calculate hue for each pixel, distribute hues over full circle (0-1 range)
            hue = i / self.pixel_count

            # Convert HSL to RGB
            pix = DotStar_Pixel(0, 0, 0, 0)
            pix.a = brightness
            pix.r, pix.g, pix.b = self._hsl_to_rgb(hue, 1.0, 0.5)

            # Append to pixel list
            pix_list.append(pix.get_pixel())

        await self._update_strip(pix_list)

    async def scroll_rainbow(self, speed: int):
        update_rate = 30
        steps_per_cycle = self.pixel_count  # One full cycle amounts to scrolling across all the pixels once
        update_interval = 1 / update_rate  # The time interval between each update

        step = 0  # Starting step

        while self.rainbow:
            pix_list = []
            brightness = 10

            hue_shift = step / steps_per_cycle  # Calculate hue shift based on current step

            for i in range(self.pixel_count):
                hue = (i / self.pixel_count + hue_shift) % 1  # Derive hue value with shift
                pix = DotStar_Pixel(0, 0, 0, 0)
                pix.a = brightness
                pix.r, pix.g, pix.b = self._hsl_to_rgb(hue, 1.0, 0.5)

                # Append to pixel list
                pix_list.append(pix.get_pixel())

            # Update strip and wait for the next update
            await self._update_strip(pix_list)
            await asyncio.sleep(update_interval)

            step = (step + speed / update_rate) % steps_per_cycle  # Advance the step for next cycle

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

    async def run(self):
        """
        This is the control loop for the DotStar Controller
        """
        # print(f"Diag: {self.diag}")
        # self.diag += 1

        if self.state == DCState.OFF:
            await self.set_solid_rgb(Pixel_Colours.get("off"))
        if self.state == DCState.ON:
            self.rainbow = True
            # need to spin the rainbow
            await self.scroll_rainbow(10)
