from machine import Pin, SPI
from ili9341 import Display, color565
from xpt2046 import Touch

# Set up SPI for display
display_spi = SPI(1, baudrate=80000000, sck=Pin(14), mosi=Pin(13))

# Set up display
display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(15), rotation=90)



# Turn on display backlight
backlight = Pin(21, Pin.OUT)
backlight.on()

# Set up back LED
red_led = Pin(4, Pin.OUT)
green_led = Pin(16, Pin.OUT)
blue_led = Pin(17, Pin.OUT)

display.draw_image(output_image.rgb)
red_led.off()