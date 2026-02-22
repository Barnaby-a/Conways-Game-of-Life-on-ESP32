from machine import Pin, SPI, ADC
import time
from ili9341 import Display, color565
from xpt2046 import Touch

# Set up SPI for display
display_spi = SPI(1, baudrate=80000000, sck=Pin(14), mosi=Pin(13))

# Set up display
display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(15))

red_led = Pin(4, Pin.OUT)
green_led = Pin(16, Pin.OUT)
blue_led = Pin(17, Pin.OUT)

# Turn on display backlight
backlight = Pin(21, Pin.OUT)
backlight.on()

# Define grid properties
display_width = 320
display_height = 240
grid_width = 20  # Number of cells horizontally
grid_height = 15  # Number of cells vertically
cell_margin = 1  # Margin between cells to create the grid effect
cell_size = (display_width - (grid_width - 1) * cell_margin) // grid_width  # Calculate cell size to fit the display

# Define colors
alive_color = color565(0, 255, 255)  # Yellow for alive cells
dead_color = color565(100, 100, 100)  # Dgray for dead cells
background_color = color565(200, 200, 200)  # Light grey for background
trail_background_color = color565(230, 230, 230)  # llgrey for trail background
button_color = color565(255, 0, 0)  # Blue for button
play_icon_color = color565(0, 255, 0)  # Green for play icon
pause_icon_color = color565(255, 255, 255)  # white for pause icon
clear_button_color = color565(0, 0, 255)  # Red for clear button
trail_button_color = color565(0, 255, 0)  # Green for trail button

# Initialize grid with all cells dead
grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

# Button properties
button_radius = 15
button_center_x = display_width - button_radius - 5  # 5 pixels from the right edge
button_center_y = display_height - button_radius - 5  #5 pixels from the bottom edge

clear_button_radius = 15
clear_button_center_x = button_center_x   # same x-coordinate as the other buttons
clear_button_center_y = button_center_y - 2 * button_radius - 5 # gap of 5 pixels between the buttons

trail_button_radius = 15
trail_button_center_x = clear_button_center_x   # same x-coordinate as the other buttons
trail_button_center_y = clear_button_center_y - 2 * clear_button_radius - 5 # gap of 5 pixels between the buttons

# Update frequency (in seconds)
update_interval = 0.1

# Function to draw a single cell
def draw_cell(row, col):
    x = col * (cell_size + cell_margin)
    y = row * (cell_size + cell_margin)
    color = alive_color if grid[row][col] == 1 else dead_color
    display.fill_rectangle(x, y, cell_size, cell_size, color)

# Function to draw the entire grid
def draw_grid():
    display.clear(background_color)  # Clear the display with the background color
    for row in range(grid_height):
        for col in range(grid_width):
            draw_cell(row, col)

def draw_grid_lines():
    for row in range(grid_height):
        for col in range(grid_width):
            x = col * (cell_size + cell_margin)
            y = row * (cell_size + cell_margin)
            display.fill_rectangle(x, y, cell_size, cell_size, background_color)

# Function to update the grid based on the Game of Life rules
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

# Function to draw the play/pause button with icon
def draw_play_pause_button():
    display.fill_circle(button_center_x, button_center_y, button_radius, button_color)
    if updating:
        # Draw pause icon
        pause_width = 6
        pause_height = 16
        gap = 4
        x1 = button_center_x - gap // 2 - pause_width
        x2 = button_center_x + gap // 2
        y1 = button_center_y - pause_height // 2
        y2 = button_center_y + pause_height // 2
        display.fill_rectangle(x1, y1, pause_width, pause_height, color565(255, 255, 255))
        display.fill_rectangle(x2, y1, pause_width, pause_height, color565(255, 255, 255))
    else:
        display.fill_polygon(3, button_center_x, button_center_y, 10, color565(255, 255, 255), 0)

# Function to draw the clear button
def draw_clear_button():
    display.fill_circle(clear_button_center_x, clear_button_center_y, clear_button_radius, clear_button_color)
    display.draw_text8x8(clear_button_center_x - 10, clear_button_center_y - 4, "A/C", color565(255, 255, 255), color565(0, 0, 255))

def draw_trail_button():
    display.fill_circle(trail_button_center_x, trail_button_center_y, trail_button_radius, trail_button_color)
    display.fill_rectangle(trail_button_center_x, trail_button_center_y - 5, 10, 10, color565(255, 255, 255))
    if not trail_on:
        display.draw_line(trail_button_center_x, trail_button_center_y - 5, trail_button_center_x - 10, trail_button_center_y - 10, color565(255, 255, 255))
        display.draw_line(trail_button_center_x, trail_button_center_y, trail_button_center_x - 10, trail_button_center_y - 5, color565(255, 255, 255))
        display.draw_line(trail_button_center_x, trail_button_center_y + 5, trail_button_center_x - 10, trail_button_center_y, color565(255, 255, 255))

# Set up SPI for touch
touch_spi = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

# Touchscreen press handler
def touchscreen_press(x, y):
    x, y = y, x  # Swap x and y due to 90-degree rotation

    global initial_screen
    if initial_screen:
        initial_screen = False
        display.clear(background_color)  # Clear the display with the background color
        led_red()
        draw_grid()
        draw_play_pause_button()
        draw_clear_button()
        draw_trail_button()
        return

    # Check if the touch is within the play/pause button
    if (x - button_center_x) ** 2 + (y - button_center_y) ** 2 <= button_radius ** 2:
        global updating
        updating = not updating
        if updating:
            led_blue()
        else:
            led_red()
        draw_play_pause_button()
        return

    # Check if the touch is within the clear button
    if (x - clear_button_center_x) ** 2 + (y - clear_button_center_y) ** 2 <= clear_button_radius ** 2:
        global trail_on
        global grid
        grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        if not trail_on:
            draw_grid()
            led_red()
        else:
            led_green()
            display.clear(trail_background_color)  # Clear the display to grey
            draw_grid_lines()
        draw_play_pause_button()
        draw_clear_button()
        draw_trail_button()
        return
    
    # Check if the touch is within the trail button
    if (x - trail_button_center_x) ** 2 + (y - trail_button_center_y) ** 2 <= trail_button_radius ** 2:
        global trail_on
        trail_on = not trail_on
        global grid
        grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        if not trail_on:
            led_red()
            draw_grid()
        else:
            led_green()
            display.clear(trail_background_color)  # Clear the display to black
            draw_grid_lines()
        draw_play_pause_button()
        draw_clear_button()
        draw_trail_button()
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
            led_blue()
            new_grid = update_grid()
            for row in range(grid_height):
                for col in range(grid_width):
                    if grid[row][col] != new_grid[row][col]:
                        grid[row][col] = new_grid[row][col]
                        draw_cell(row, col)
        time.sleep(update_interval)

except KeyboardInterrupt:
    print("\nCtrl-C pressed. Cleaning up and exiting...")
finally:
    display.cleanup()