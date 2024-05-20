import os
import time
import numpy as np
from PIL import Image
import mss
from openai import OpenAI
import base64

# Define the regions to capture (adjust these coordinates based on your screen setup)
regions = [
    {"top": 0, "left": 0, "width": 960, "height": 540},    # Top-left quarter
    {"top": 0, "left": 960, "width": 960, "height": 540},  # Top-right quarter
    {"top": 540, "left": 0, "width": 960, "height": 540},  # Bottom-left quarter
    {"top": 540, "left": 960, "width": 960, "height": 540}  # Bottom-right quarter
]

# Path to save the images
image_folder_path = 'img'
confirmed_image_folder_path = 'confirmed_img'
os.makedirs(image_folder_path, exist_ok=True)
os.makedirs(confirmed_image_folder_path, exist_ok=True)

# Initialize the screenshot grabber
sct = mss.mss()

# Instantiate the OpenAI client
client = OpenAI(
    api_key='Your_OPENAI_KEY')
MODEL = "gpt-4o"

# Function to capture a screenshot of a specific region


def capture_screenshot(region):
    try:
        screenshot = sct.grab(region)
        img = Image.frombytes(
            'RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        return img
    except Exception as e:
        print(f"Error capturing screenshot for region {region}: {e}")
        return None


def has_significant_change(img1, img2, threshold=0.05):
    if img1 is None or img2 is None:
        return False
    img1_np = np.array(img1)
    img2_np = np.array(img2)
    difference = np.abs(img1_np - img2_np)
    change = np.mean(difference) / 255
    return change > threshold

# Function to cleanup images


def cleanup():
    for filename in os.listdir(image_folder_path):
        file_path = os.path.join(image_folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

# Function to encode image to base64


def encode_image(compressed_image_path):
    with open(compressed_image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to confirm world boss using GPT-4 API


def confirm_world_boss(current_image):
    print("Sending current image and prompt to GPT-4 for confirmation...")

    # Resize and compress the current image
    # compressed_image = resize_and_compress_image(current_image)
    pending_image = current_image

    # Save the compressed image to visualize later
    pending_image_path = os.path.join(
        image_folder_path, "pending_image.png")
    pending_image.save(pending_image_path)

    # Encode the compressed image to base64
    base64_image = encode_image(pending_image_path)
    # Debugging line to check the length
    print(f"Base64 image length: {len(base64_image)}")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with image recognition task."},
            {"role": "user", "content": [
                {"type": "text", "text": "Can you see a world boss from War of Warcraft Classic Era in attached image? \
                 World boss including Azuregos, Kazzak, Emeriss, Lethon, Taerar, Ysondre. \
                 You need to pay extra attention if image is in Azshara. \
                 Spirit of Azuregos doesn't consider as world boss. Compare to Azuregos, spirit of Azuregos is transparent and in ghost form.\
                 If you see a world boss, just return 'yes' followed by the boss name, otherwise 'no'."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                 }
            ]}
        ],
        temperature=0.0,
    )

    print("text response", response.choices[0].message.content)

    if 'yes' in response.choices[0].message.content.lower():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        confirmed_image_path = os.path.join(
            confirmed_image_folder_path, f"confirmed_image_{timestamp}.png")
        pending_image.save(confirmed_image_path)
        print(f"Image saved to {confirmed_image_path}")


try:
    # Initial setup: Capture the initial screenshots
    initial_screenshots = [capture_screenshot(region) for region in regions]

    # Save initial screenshots for verification
    for i, screenshot in enumerate(initial_screenshots):
        if screenshot:
            screenshot.save(os.path.join(image_folder_path,
                            f"initial_screenshot_{i+1}.png"))
            screenshot.save(os.path.join(
                image_folder_path, f"previous_screenshot_{i+1}.png"))

    # Monitor and compare screenshots in a loop
    previous_screenshots = initial_screenshots.copy()

    running = True
    while running:
        try:
            time.sleep(10)  # Check every 10 seconds

            for i, region in enumerate(regions):
                current_screenshot = capture_screenshot(region)

                if has_significant_change(previous_screenshots[i], current_screenshot) or has_significant_change(initial_screenshots[i], current_screenshot):
                    print(f"Significant change detected in region {i + 1}")
                    if confirm_world_boss(current_screenshot):
                        print(f"World boss confirmed in region {i + 1}")

                # Save the current screenshot as the previous screenshot
                if current_screenshot:
                    current_screenshot.save(os.path.join(
                        image_folder_path, f"previous_screenshot_{i+1}.png"))

                # Update the previous screenshot
                previous_screenshots[i] = current_screenshot

        except KeyboardInterrupt:
            running = False

except KeyboardInterrupt:
    print("Script interrupted by user.")
finally:
    cleanup()
    print("Cleanup completed. All files in the img folder have been deleted.")
