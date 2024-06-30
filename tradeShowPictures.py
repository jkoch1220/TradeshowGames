import pygame
import random
import time
import qrcode
from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError
import json
import os
from pylibdmtx.pylibdmtx import encode as dmtx_encode
import numpy as np

# Initialize pygame
pygame.init()

# Constants
FONT_SIZE = 32
CODE_COUNT = 1
CODE_WIDTH = 100  # Width for the codes
CODE_HEIGHT_1D = 200  # Height for 1D codes
CODE_HEIGHT_2D = 100  # Height for 2D codes
MARGIN = 50  # Margin to ensure codes are within the field of view

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Setup the screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Code Typing Game")

# Font
font = pygame.font.Font(None, FONT_SIZE)
large_font = pygame.font.Font(None, 48)

# Load sounds
pygame.mixer.init()
success_sound = pygame.mixer.Sound('tradeshow/success.mp3')
success_sound.set_volume(1.0)  # Full volume for success sound
error_sound = pygame.mixer.Sound('tradeshow/error.mp3')
error_sound.set_volume(1.0)  # Full volume for error sound

# Load background music
pygame.mixer.music.load('tradeshow/background.mp3')
pygame.mixer.music.set_volume(0.3)  # Lower volume for background music
pygame.mixer.music.play(-1)  # Loop the background music indefinitely

# Game states
START_SCREEN = 0
GAME_RUNNING = 1
GAME_OVER = 2
SHOW_LEADERBOARD = 3

# Initial state
game_state = START_SCREEN

# Datamatrix code for START
start_code_text = "START"
start_code_image = None

# Codes and positions
codes = []
positions = []
code_images = []
code_types = []
leaderboard = []

def load_leaderboard():
    global leaderboard
    try:
        with open('leaderboard.json', 'r') as file:
            leaderboard = json.load(file)
    except FileNotFoundError:
        leaderboard = []

def save_leaderboard():
    with open('leaderboard.json', 'w') as file:
        json.dump(leaderboard, file)

def apply_noise(image):
    noise = np.random.randint(0, 100, (image.height, image.width), dtype='uint8')
    noise_image = Image.fromarray(noise, mode='L')
    image = Image.blend(image, noise_image, 0.2)
    return image

def apply_random_rotation(image):
    angle = random.uniform(-30, 30)  # Random angle between -30 and 30 degrees
    rotated_image = image.rotate(angle, expand=True, fillcolor=(255, 255, 255, 0))
    return rotated_image

def generate_datamatrix(data, damaged=False):
    dmtx = dmtx_encode(data.encode('utf-8'))
    img = Image.frombytes('RGB', (dmtx.width, dmtx.height), dmtx.pixels)
    img = img.convert('RGBA')
    if damaged:
        img = img.filter(ImageFilter.GaussianBlur(radius=2))  # Gaussian blur
        img = apply_noise(img)  # Add noise
        img = img.transpose(Image.FLIP_LEFT_RIGHT)  # Horizontal flip
    img = img.resize((CODE_WIDTH, CODE_HEIGHT_2D), Image.LANCZOS)
    img = apply_random_rotation(img)  # Apply random rotation
    return img

def pil_to_surface(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    image = Image.frombytes(mode, size, data)
    image = image.convert("RGBA")
    raw_str = image.tobytes("raw", "RGBA")
    return pygame.image.fromstring(raw_str, size, "RGBA")

def load_code_images(directory):
    code_images = []
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory {directory} does not exist.")
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for image_file in image_files:
        try:
            img = Image.open(os.path.join(directory, image_file)).convert('RGBA')
            img = img.resize((CODE_WIDTH, CODE_HEIGHT_2D), Image.LANCZOS)
            code_images.append(pil_to_surface(img))
        except UnidentifiedImageError:
            print(f"Cannot identify image file {os.path.join(directory, image_file)}. Skipping.")
    return code_images

def reset_game(damaged_codes=False):
    global codes, start_code_image, positions, code_images, code_types, start_time, code_index, input_text
    codes = [f"CODE{i+1}" for i in range(CODE_COUNT)]  # Use placeholder codes
    positions = [(random.randint(MARGIN, SCREEN_WIDTH - CODE_WIDTH - MARGIN), random.randint(MARGIN, SCREEN_HEIGHT - CODE_HEIGHT_2D - MARGIN)) for _ in range(CODE_COUNT)]
    
    # Load code images from the codepictures directory
    code_images = load_code_images(r'C:\Users\julikoch\Workplace\tradeshow\codepictures')
    if len(code_images) < CODE_COUNT:
        raise ValueError("Not enough images in the codepictures directory.")
    
    # Generate start button as a datamatrix code
    start_button_code = generate_datamatrix("START")
    start_button_image = pil_to_surface(start_button_code)
    
    start_time = time.time()
    code_index = 0
    input_text = ""
    
    return start_button_image

# Load leaderboard
load_leaderboard()

# Start button
start_button_image = reset_game()

# Main loop
running = True
input_text = ""
name_input = ""
show_green_screen = False
green_screen_start_time = 0
GREEN_SCREEN_DURATION = 0.5
show_red_screen = False
red_screen_start_time = 0
RED_SCREEN_DURATION = 0.5

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == START_SCREEN:
            if event.type == pygame.KEYDOWN:
                # Handle keyboard input
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    # Check if input text matches start code
                    if input_text.strip().upper() == start_code_text:
                        game_state = GAME_RUNNING
                        input_text = ""
                else:
                    input_text += event.unicode
        
        elif game_state == GAME_RUNNING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    print(f"Expected: {codes[code_index]}")
                    print(f"Entered: {input_text.strip()}")
                    if input_text.strip() == codes[code_index]:
                        code_index += 1
                        input_text = ""
                        success_sound.play()
                        show_green_screen = True
                        green_screen_start_time = time.time()
                        if code_index == CODE_COUNT:
                            game_state = GAME_OVER
                            end_time = time.time()
                    else:
                        input_text = ""
                        error_sound.play()
                        show_red_screen = True
                        red_screen_start_time = time.time()
                else:
                    input_text += event.unicode

        elif game_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if name_input:
                        leaderboard.append({"name": name_input, "time": end_time - start_time})
                        leaderboard = sorted(leaderboard, key=lambda x: x["time"])[:10]
                        save_leaderboard()
                        game_state = SHOW_LEADERBOARD
                else:
                    name_input += event.unicode

        elif game_state == SHOW_LEADERBOARD:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = START_SCREEN
    
    if game_state == START_SCREEN:
        screen.blit(start_button_image, (SCREEN_WIDTH // 2 - CODE_WIDTH // 2, SCREEN_HEIGHT // 2 - CODE_HEIGHT_2D // 2))
        input_text_surface = font.render(input_text, True, BLACK)
        screen.blit(input_text_surface, (10, 10))
    
    elif game_state == GAME_RUNNING:
        if show_green_screen:
            if time.time() - green_screen_start_time < GREEN_SCREEN_DURATION:
                screen.fill(GREEN)
            else:
                show_green_screen = False
        
        if show_red_screen:
            if time.time() - red_screen_start_time < RED_SCREEN_DURATION:
                screen.fill(RED)
            else:
                show_red_screen = False
        x, y = positions[code_index]
        screen.blit(code_images[code_index], (x, y))
        code_text_surface = font.render(codes[code_index], True, BLACK)
        screen.blit(code_text_surface, (x, y + CODE_HEIGHT_2D + 10))
        input_text_surface = font.render(input_text, True, BLACK)
        screen.blit(input_text_surface, (10, 10))
    
    elif game_state == GAME_OVER:
        time_taken = end_time - start_time
        result_text = font.render(f"Time: {time_taken:.2f} seconds", True, BLACK)
        screen.blit(result_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 75))
        name_prompt = font.render("Enter your name:", True, BLACK)
        screen.blit(name_prompt, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        name_input_surface = font.render(name_input, True, BLACK)
        screen.blit(name_input_surface, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30))

    elif game_state == SHOW_LEADERBOARD:
        screen.fill(WHITE)
        leaderboard_title = large_font.render("Leaderboard", True, BLACK)
        screen.blit(leaderboard_title, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 150))
        for idx, entry in enumerate(leaderboard):
            name = entry["name"]
            time_taken = entry["time"]
            leaderboard_text = font.render(f"{idx + 1}. {name} - {time_taken:.2f} seconds", True, BLACK)
            screen.blit(leaderboard_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100 + idx * 30))
        continue_text = font.render("Press Enter to return to the start screen", True, BLACK)
        screen.blit(continue_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 50))

    pygame.display.flip()

pygame.quit()
