import spidev

num_pixels = 120
brightness = 0  # Range of brightness is 0-31
red = 163
green = 28
blue = 109

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000

# Create an empty payload
data = [0x00, 0x00, 0x00, 0x00]

# Set up the color of each LED in the chain
for i in range(num_pixels):
    data.append(
        0b11100000 | brightness)  # The first three bits must be 1, and the last five bits control the brightness
    data.append(blue)  # Blue color first
    data.append(green)  # Green color second
    data.append(red)  # Red color last

# End frame of 32 zero bits (0x00)
data.append(0x00)
data.append(0x00)
data.append(0x00)
data.append(0x00)
data.append(0x00)

# Send data
spi.xfer2(data)