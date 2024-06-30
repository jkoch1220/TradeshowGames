import pygame
import random
import time
import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageFilter, ImageOps
import json
from pylibdmtx.pylibdmtx import encode as dmtx_encode, decode as dmtx_decode
import pyqrcode
import pdf417gen
import io
import numpy as np

# Initialize pygame
pygame.init()

# Constants
FONT_SIZE = 32
CODE_COUNT = 10

CODE_WIDTH = 100  # Reduced width for the codes

CODE_WIDTH_1D = 100  # Height for 1D codes
CODE_WIDTH_2D = 100  # Height for 2D codes

CODE_HEIGHT = 100  # Reduced height for the codes

CODE_HEIGHT_1D = 50  # Height for 1D codes
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

def generate_code():
    return ''.join(random.choices('0123456789', k=12))  # Generate 12 digits

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
    img = img.resize((CODE_WIDTH, CODE_HEIGHT), Image.LANCZOS)
    img = apply_random_rotation(img)  # Apply random rotation
    return img

def generate_aztec_code(data, damaged=False):
    qr = pyqrcode.create(data, error='L', version=1, mode='binary')
    buffer = io.BytesIO()
    qr.png(buffer, scale=10)
    buffer.seek(0)
    img = Image.open(buffer).convert('RGBA')
    if damaged:
        img = img.filter(ImageFilter.GaussianBlur(radius=2))  # Gaussian blur
        img = apply_noise(img)  # Add noise
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # Vertical flip
    img = img.resize((CODE_WIDTH, CODE_HEIGHT), Image.LANCZOS)
    img = apply_random_rotation(img)  # Apply random rotation
    return img

def generate_pdf417(data, damaged=False):
    codes = pdf417gen.encode(data, columns=5)  # Example adjustment, change columns as needed
    img = pdf417gen.render_image(codes).convert('RGBA')
    if damaged:
        img = img.filter(ImageFilter.GaussianBlur(radius=2))  # Gaussian blur
        img = apply_noise(img)  # Add noise
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # Vertical flip
    img = img.resize((CODE_WIDTH_1D, CODE_HEIGHT_1D), Image.Resampling.LANCZOS)
    img = apply_random_rotation(img)  # Apply random rotation
    return img

def generate_barcode(data, barcode_type='code128', damaged=False):
    barcode_class = barcode.get_barcode_class(barcode_type)
    code = barcode_class(data, writer=ImageWriter())
    barcode_image = code.render(writer_options={"module_width": 0.5, "module_height": 50, "quiet_zone": 2})
    barcode_image = barcode_image.convert('RGBA')
    if damaged:
        barcode_image = barcode_image.filter(ImageFilter.GaussianBlur(radius=2))  # Gaussian blur
        barcode_image = apply_noise(barcode_image)  # Add noise
        barcode_image = barcode_image.transpose(Image.FLIP_LEFT_RIGHT)  # Horizontal flip
    barcode_image = barcode_image.resize((CODE_WIDTH_1D, CODE_HEIGHT_1D), Image.LANCZOS)
    return barcode_image

def generate_upcean(data, damaged=False):
    EAN13 = barcode.get_barcode_class('ean13')
    code = EAN13(data, writer=ImageWriter())
    barcode_image = code.render(writer_options={"module_width": 0.5, "module_height": 50, "quiet_zone": 2})
    barcode_image = barcode_image.convert('RGBA')
    if damaged:
        barcode_image = barcode_image.filter(ImageFilter.GaussianBlur(radius=2))  # Gaussian blur
        barcode_image = apply_noise(barcode_image)  # Add noise
        barcode_image = barcode_image.transpose(Image.FLIP_LEFT_RIGHT)  # Horizontal flip
    barcode_image = barcode_image.resize((CODE_WIDTH_1D, CODE_HEIGHT_1D), Image.LANCZOS)
    return barcode_image

def generate_msi(data, damaged=False):
    try:
        code = barcode.get_barcode_class('msi')
        msi_code = code(data, writer=ImageWriter())
        barcode_image = msi_code.render(writer_options={"module_width": 0.5, "module_height": 50, "quiet_zone": 2})
        barcode_image = barcode_image.convert('RGBA')
        if damaged:
            barcode_image = barcode_image.filter(ImageFilter.GaussianBlur(radius=2))  # Gaussian blur
            barcode_image = apply_noise(barcode_image)  # Add noise
            barcode_image = barcode_image.transpose(Image.FLIP_TOP_BOTTOM)  # Vertical flip
        barcode_image = barcode_image.resize((CODE_WIDTH_1D, CODE_HEIGHT_1D), Image.LANCZOS)
        return barcode_image
    except barcode.errors.BarcodeNotFoundError:
        print(f"Barcode type 'msi' is not supported. Generating default barcode instead.")
        return generate_barcode(data, damaged=damaged)


def pil_to_surface(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    image = Image.frombytes(mode, size, data)
    image = image.convert("RGBA")
    raw_str = image.tobytes("raw", "RGBA")
    return pygame.image.fromstring(raw_str, size, "RGBA")

def reset_game(damaged_codes=False):
    global codes, start_code_image, positions, code_images, code_types, start_time, code_index, input_text
    codes = [generate_code() for _ in range(CODE_COUNT)]
    positions = [(random.randint(MARGIN, SCREEN_WIDTH - CODE_WIDTH - MARGIN), random.randint(MARGIN, SCREEN_HEIGHT - CODE_HEIGHT - MARGIN)) for _ in range(CODE_COUNT)]
    code_images = []
    code_types = []
    
    # Generate codes for the game
    for code in codes:
        code_type = random.choices(['datamatrix', 'aztec', 'code128', 'pdf417', 'upcean', 'msi'], 
                                   weights=[30, 10, 10, 10, 10, 10], k=1)[0]
        if code_type == 'datamatrix':
            code_image = generate_datamatrix(code, damaged=damaged_codes)
        else:
            code_image = generate_aztec_code(code, damaged=damaged_codes)

        code_images.append(pil_to_surface(code_image))
        code_types.append(code_type)
    
    # Generate start button as a datamatrix code
    start_button_code = generate_datamatrix("START")
    start_button_image = pil_to_surface(start_button_code)
    
    start_time = time.time()
    code_index = 0
    input_text = ""
    
    return start_button_image

reset_game()

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

# Load background image
background_image = pygame.image.load(r'C:\Users\julikoch\Workplace\tradeshow\background.jpg').convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

while running:
    screen.blit(background_image, (0, 0))  # Blit the background image first

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
        screen.blit(start_button_image, (SCREEN_WIDTH // 2 - CODE_WIDTH // 2, SCREEN_HEIGHT // 2 - CODE_HEIGHT // 2))
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
        screen.blit(continue_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 50))

    pygame.display.flip()

pygame.quit()
   