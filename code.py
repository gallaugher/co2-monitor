# C02 Sensor in CircuitPython
# Uses an Adafruit SCD40 C02 Sensor & an
# Adafruit 1.5" OLED 128 x 128 gray scale display (STEMMA-QT)
# This code is running on a QT Py ESP32-S2, but should work
# identically on any board with a STEMMA-QT port

import board, time
import adafruit_scd4x
import displayio, terminalio, adafruit_ssd1327
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

displayio.release_displays()

# Use for I2C
i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)

WIDTH = 128
HEIGHT = 128
BORDER = 0 # was 8
FONTSCALE = 2 # was 1

display = adafruit_ssd1327.SSD1327(display_bus, width=WIDTH, height=HEIGHT)

# Setup C02 Sensor
# i2c = board.STEMMA_I2C() # uses board.SCL and board.SDA
scd4x = adafruit_scd4x.SCD4X(i2c)
print("Serial number:", [hex(i) for i in scd4x.serial_number])

scd4x.start_periodic_measurement()
print("Waiting for first measurement....")


def normal_update_text(c02, temp, humidity, background_color, font_color, level):
    # Make the display context
    splash = displayio.Group()
    display.show(splash)

    # Draw a background rectangle, but not the full display size
    color_bitmap = displayio.Bitmap(
        display.width, display.height, 1
    )
    color_palette = displayio.Palette(1)
    color_palette[0] = background_color  # BLACK
    bg_sprite = displayio.TileGrid(
        color_bitmap, pixel_shader=color_palette, x=0, y=0
    )
    splash.append(bg_sprite)

    # Draw some label text
    VERTICAL_MOVE = 5
    co2_label_text_area = label.Label(terminalio.FONT, text=f"CO2 ppm: {level}", color=font_color, x=8, y=5+VERTICAL_MOVE)
    splash.append(co2_label_text_area)
    font = bitmap_font.load_font("fonts/Verdana-Bold-20.bdf")
    c02_text = label.Label(font, text=c02, scale=2, color=font_color, x=9, y=28+VERTICAL_MOVE)
    splash.append(c02_text)
    temp_label_area = label.Label(terminalio.FONT, text="Temp:", color=font_color, x=7, y=53+VERTICAL_MOVE)
    splash.append(temp_label_area)
    temp_text = label.Label(terminalio.FONT, text=temp, scale=2, color=font_color, x=12, y=70+VERTICAL_MOVE)
    splash.append(temp_text)

    hum_label_area = label.Label(terminalio.FONT, text="Humid:", color=font_color, x=7, y=88+VERTICAL_MOVE)
    splash.append(hum_label_area)
    hum_text = label.Label(terminalio.FONT, text=humidity, scale=2, color=font_color, x=12, y=104+VERTICAL_MOVE)
    splash.append(hum_text)

while True:
    if scd4x.data_ready:
        print(f"C02 = {scd4x.CO2}")
        c02 = f"{scd4x.CO2}"
        temp_val = (scd4x.temperature * (9/5)) + 32
        print(f"Temperature: {temp_val:.0f}")
        temp = f"{temp_val:.0f} F"
        print(f"Humidity: {scd4x.relative_humidity:.1f} %\n")
        humidity = f"{scd4x.relative_humidity:.1f} %"
        if scd4x.CO2 < 1000:
            normal_update_text(c02, temp, humidity, 0x000000, 0xFFFFFF, "good")
        else:
            normal_update_text(c02, temp, humidity, 0xFFFFFF, 0x000000, "HIGH")
    time.sleep(4)

