from machine import Pin, SPI
from ili9341 import Display, color565
from xpt2046 import Touch

# Set up SPI for display
display_spi = SPI(1, baudrate=80000000, sck=Pin(14), mosi=Pin(13))

# Set up display
display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(15), rotation=0)



# Turn on display backlight
backlight = Pin(21, Pin.OUT)
backlight.on()

# Set up back LED
red_led = Pin(4, Pin.OUT)
green_led = Pin(16, Pin.OUT)
blue_led = Pin(17, Pin.OUT)

# Define grid properties
display_width = 240
display_height = 320
grid_pixel_width = 130  # Width of the grid in pixels
grid_pixel_height = 260  # Height of the grid in pixels
grid_width = 10  # Number of cells horizontally
grid_height = 20  # Number of cells vertically
cell_margin = 1  # Margin between cells to create the grid effect
cell_size = (grid_pixel_width - (grid_width - 1) * cell_margin) // grid_width  # Calculate cell size to fit the grid

# Define colors
piece_I = color565(255, 255, 0)  # Cyan for I piece
piece_O = color565(0, 255, 255)  # Yellow for alive cells
piece_T = color565(255, 0, 255)  # Magenta for T piece
piece_S = color565(0, 255, 0)  # Green for S piece
piece_Z = color565(0, 0, 255)  # Red for Z piece
piece_L = color565(255, 165, 0)  # Orange for L piece
piece_J = color565(255, 0, 0)  # Blue for J piece
dead_cells = color565(0, 0, 0)  # Black for dead cells
background_color = color565(100, 100, 100)  # Dgrey for background

# Initialize grid with all cells dead
grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]


# Function to draw a single cell
def draw_cell(row, col, color):
    x = col * (cell_size + cell_margin)
    y = row * (cell_size + cell_margin)
    color = color if grid[row][col] == 1 else dead_cells
    display.fill_rectangle(x, y, cell_size, cell_size, color)

# Function to draw the entire grid
def draw_grid():
    display.clear(background_color)  # Clear the display with the background color
    for row in range(grid_height):
        for col in range(grid_width):
            draw_cell(row, col)


# Function to update the grid based on the Tetris rules
def update_grid():
    new_grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
    for row in range(grid_height):
        for col in range(grid_width):
            live_neighbors = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    r = (row + i + grid_height) % grid_height
                    c = (col + j + grid_width) % grid_width
                    live_neighbors += grid[r][c]
            if grid[row][col] == 1 and (live_neighbors < 2 or live_neighbors > 3):
                new_grid[row][col] = 0
            elif grid[row][col] == 0 and live_neighbors == 3:
                new_grid[row][col] = 1
            else:
                new_grid[row][col] = grid[row][col]
    return new_grid



# Set up SPI for touch
touch_spi = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

# Touchscreen press handler
def touchscreen_press(x, y):
    x, y = y, x  # Swap x and y due to 90-degree rotation

    global initial_screen
    if initial_screen:
        initial_screen = False
        display.clear(background_color)  # Clear the display with the background color
        return

    row = y // (cell_size + cell_margin)
    col = x // (cell_size + cell_margin)

    if 0 <= col < grid_width and 0 <= row < grid_height:
        # Toggle cell state
        grid[row][col] = 1 if grid[row][col] == 0 else 0
        draw_cell(row, col)

def led_red():
    red_led.off()
    green_led.on()
    blue_led.on()  
def led_green():
    red_led.on()
    green_led.off()
    blue_led.on()
def led_blue():
    red_led.on()
    green_led.on()
    blue_led.off()
def led_white():
    red_led.off()
    green_led.off()
    blue_led.off()


# Set up touch
touch = Touch(touch_spi, cs=Pin(33), int_pin=Pin(36), int_handler=touchscreen_press)

# Main loop to keep the program running
updating = False
trail_on = False
initial_screen = True
try:
    # Initial draw
    display.clear(color565(0, 0, 0))  # Clear the display with the background color
    display.draw_text8x8(112, 10, "Game of Life", color565(255, 255, 255))
    display.draw_text8x8(68, 30, "Press anywhere to start", color565(255, 255, 255))
    display.draw_text8x8(10, 50, "Rules:", color565(255, 255, 255))
    display.draw_text8x8(10, 60, "1. Any live cell with fewer than", color565(255, 255, 255))
    display.draw_text8x8(34, 70, "two live neighbors dies", color565(255, 255, 255))
    display.draw_text8x8(10, 80, "2. Any live cell with two or", color565(255, 255, 255))
    display.draw_text8x8(34, 90, "three live neighbors lives on", color565(255, 255, 255))
    display.draw_text8x8(10, 100, "3. Any live cell with more than", color565(255, 255, 255))
    display.draw_text8x8(34, 110, "three live neighbors dies", color565(255, 255, 255))
    display.draw_text8x8(10, 120, "4. Any dead cell with exactly three", color565(255, 255, 255))
    display.draw_text8x8(34, 130, "live neighbors becomes a live cell", color565(255, 255, 255))
    display.draw_text8x8(10, 150, "How To Play:", color565(255, 255, 255))
    display.draw_text8x8(10, 160, "1. Touch to toggle cells", color565(255, 255, 255))
    display.draw_text8x8(10, 170, "2. Press the button to start/stop", color565(255, 255, 255))
    display.draw_text8x8(10, 180, "3. Enjoy the game!", color565(255, 255, 255))
    display.draw_text8x8(68, 200, "Press anywhere to start", color565(255, 255, 255))
    display.draw_text8x8(10, 220, "Created by: Barnaby-a", color565(255, 255, 255))
    led_white()
    
    while True:
        touch.get_touch()
        if updating:
            draw_shape()
            new_grid = update_grid()
            for row in range(grid_height):
                for col in range(grid_width):
                    if grid[row][col] != new_grid[row][col]:
                        grid[row][col] = new_grid[row][col]
                        draw_cell(row, col)
     

except KeyboardInterrupt:
    print("\nCtrl-C pressed. Cleaning up and exiting...")
finally:
    display.cleanup()