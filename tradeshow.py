import pygame
import random
import time
import qrcode
import numpy as np
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import json

# Initialize pygame
pygame.init()

# Constants
FONT_SIZE = 32
CODE_COUNT = 10
CODE_WIDTH = 200  # Fixed width for the codes
CODE_HEIGHT = 200  # Fixed height for the codes
MARGIN = 50  # Margin to ensure codes are within the field of view

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Setup the screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Code Typing Game")

# Font
font = pygame.font.Font(None, FONT_SIZE)
large_font = pygame.font.Font(None, 48)

# Load sounds
pygame.mixer.init()
success_sound = pygame.mixer.Sound('success.mp3')
success_sound.set_volume(1.0)  # Full volume for success sound

# Load background music
pygame.mixer.music.load('background.mp3')
pygame.mixer.music.set_volume(0.3)  # Lower volume for background music
pygame.mixer.music.play(-1)  # Loop the background music indefinitely

# Game states
START_SCREEN = 0
GAME_RUNNING = 1
GAME_OVER = 2
SHOW_LEADERBOARD = 3

# Initial state
game_state = START_SCREEN

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

def generate_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img = img.resize((CODE_WIDTH, CODE_HEIGHT), Image.Resampling.LANCZOS)
    return img

def generate_barcode(data):
    CODE128 = barcode.get_barcode_class('code128')
    code = CODE128(data, writer=ImageWriter())
    barcode_image = code.render(writer_options={"module_width": 0.5, "module_height": 50, "quiet_zone": 2})
    barcode_image = barcode_image.resize((CODE_WIDTH, CODE_HEIGHT), Image.Resampling.LANCZOS)
    return barcode_image

def pil_to_surface(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    image = Image.frombytes(mode, size, data)
    image = image.convert("RGBA")
    raw_str = image.tobytes("raw", "RGBA")
    return pygame.image.fromstring(raw_str, size, "RGBA")

def reset_game():
    global codes, positions, code_images, code_types, start_time, code_index, input_text
    codes = [generate_code() for _ in range(CODE_COUNT)]
    positions = [(random.randint(MARGIN, SCREEN_WIDTH - CODE_WIDTH - MARGIN), random.randint(MARGIN, SCREEN_HEIGHT - CODE_HEIGHT - MARGIN)) for _ in range(CODE_COUNT)]
    code_images = []
    code_types = []
    for code in codes:
        if random.choice([True, False]):
            code_image = generate_qr_code(code)
            code_images.append(pil_to_surface(code_image))
            code_types.append('2d')
        else:
            code_image = generate_barcode(code)
            code_images.append(pil_to_surface(code_image))
            code_types.append('1d')
    start_time = time.time()
    code_index = 0
    input_text = ""

reset_game()
load_leaderboard()

# Start button
start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)

# Main loop
running = True
input_text = ""
name_input = ""
show_green_screen = False
green_screen_start_time = 0
GREEN_SCREEN_DURATION = 0.5

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == START_SCREEN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_state = GAME_RUNNING
                    reset_game()
        
        elif game_state == GAME_RUNNING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if input_text == codes[code_index]:
                        code_index += 1
                        input_text = ""
                        success_sound.play()
                        show_green_screen = True
                        green_screen_start_time = time.time()
                        if code_index == CODE_COUNT:
                            game_state = GAME_OVER
                            end_time = time.time()
                    else:
                        input_text += event.unicode
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
        pygame.draw.rect(screen, BLACK, start_button)
        text = large_font.render("START", True, WHITE)
        text_rect = text.get_rect(center=start_button.center)
        screen.blit(text, text_rect)
    
    elif game_state == GAME_RUNNING:
        if show_green_screen:
            if time.time() - green_screen_start_time < GREEN_SCREEN_DURATION:
                screen.fill(GREEN)
            else:
                show_green_screen = False
        x, y = positions[code_index]
        screen.blit(code_images[code_index], (x, y))
        code_text_surface = font.render(codes[code_index], True, BLACK)
        screen.blit(code_text_surface, (x, y + CODE_HEIGHT + 10))
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
        screen.blit(continue_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 150))

    pygame.display.flip()

pygame.quit()
