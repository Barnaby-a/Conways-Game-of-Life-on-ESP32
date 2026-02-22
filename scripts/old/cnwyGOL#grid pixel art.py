from machine import Pin, SPI, ADC
import time
from ili9341 import Display, color565
from xpt2046 import Touch

# Set up SPI for display
display_spi = SPI(1, baudrate=80000000, sck=Pin(14), mosi=Pin(13))

# Set up display
display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(15))

# Turn on display backlight
backlight = Pin(21, Pin.OUT)
backlight.on()

# Define grid properties
cell_size = 16
grid_width = 20  # Number of cells horizontally
grid_height = 15  # Number of cells vertically

# Define colors
color1 = color565(126, 126, 126)  # grey
color2 = color565(0, 255, 255)  # yellow
line_color = color565(200, 200, 200)  # black

# Initialize grid with default color
grid = [[color1 for _ in range(grid_width)] for _ in range(grid_height)]

# Function to draw the grid lines
def draw_grid_lines():
    # Draw vertical grid lines
    for col in range(grid_width + 1):
        x = col * cell_size
        display.draw_vline(x, 0, grid_height * cell_size, line_color)

    # Draw horizontal grid lines
    for row in range(grid_height + 1):
        y = row * cell_size
        display.draw_hline(0, y, grid_width * cell_size, line_color)

# Draw initial grid
for row in range(grid_height):
    for col in range(grid_width):
        x = col * cell_size
        y = row * cell_size
        display.fill_rectangle(x, y, cell_size, cell_size, grid[row][col])

# Draw grid lines on top of the cells
draw_grid_lines()

# Set up SPI for touch
touch_spi = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

# Touchscreen press handler
def touchscreen_press(x, y):
    x, y = y, x  # Swap x and y due to 90-degree rotation

    # Debug print to verify touch coordinates
    print(f"Touch coordinates: x={x}, y={y}")

    row = y // cell_size
    col = x // cell_size
    print(f"Grid coordinates: row={row}, col={col}")  # Debug print to verify grid coordinates

    if 0 <= col < grid_width and 0 <= row < grid_height:
        # Toggle cell color
        grid[row][col] = color2 if grid[row][col] == color1 else color1
        display.fill_rectangle(col * cell_size, row * cell_size, cell_size, cell_size, grid[row][col])
        # Redraw grid lines for the toggled cell
        draw_grid_lines()

# Set up touch
touch = Touch(touch_spi, cs=Pin(33), int_pin=Pin(36), int_handler=touchscreen_press)

# Main loop to keep the program running
try:
    while True:
        touch.get_touch()
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nCtrl-C pressed. Cleaning up and exiting...")
finally:
    display.cleanup()