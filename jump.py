import time
import pyautogui

# Define the regions to capture (adjust these coordinates based on your screen setup)
regions = [
    {"top": 0, "left": 0, "width": 960, "height": 540},    # Top-left quarter
    {"top": 0, "left": 960, "width": 960, "height": 540},  # Top-right quarter
    {"top": 540, "left": 0, "width": 960, "height": 540},  # Bottom-left quarter
    {"top": 540, "left": 960, "width": 960, "height": 540}  # Bottom-right quarter
]


def move_cursor_click_and_press_space(region):
    # Calculate the center of the region
    center_x = region["left"] + region["width"] // 2
    center_y = region["top"] + region["height"] // 2

    # Move the cursor to the center of the region
    pyautogui.moveTo(center_x, center_y)

    # Perform a left mouse click
    pyautogui.click()

    # Press the spacebar
    pyautogui.press('space')


try:
    while True:
        for region in regions:
            move_cursor_click_and_press_space(region)
            # Wait for 10 seconds before moving to the next region
            time.sleep(10)
except KeyboardInterrupt:
    print("Script interrupted by user.")
