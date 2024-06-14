import pygame
import random
import os
from pylibdmtx.pylibdmtx import encode
from io import BytesIO
from PIL import Image

# Initialize pygame
pygame.init()

# Constants
FONT_SIZE = 32
COLUMNS = 6  # Number of columns to display DataMatrix codes

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize the screen in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Music Code Game")
WIDTH, HEIGHT = screen.get_size()

# Configure mixer for better sound quality
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

# Path to the keys directory
keys_dir = os.path.join(os.path.dirname(__file__), 'keys')

# Load sounds
sounds = {}
for idx in range(24):
    key_code = f"KEY{idx+1:02d}"
    file_path = os.path.join(keys_dir, f"key{idx+1:02d}.mp3")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No file '{file_path}' found in working directory.")
    sounds[key_code] = pygame.mixer.Sound(file_path)

# Generate DataMatrix codes
codes = list(sounds.keys())
random.shuffle(codes)

# Font
font = pygame.font.Font(None, FONT_SIZE)

# Function to create DataMatrix image
def create_datamatrix_image(data):
    encoded = encode(data.encode('utf-8'))
    image = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    with BytesIO() as output:
        image.save(output, format="BMP")
        output.seek(0)
        return pygame.image.load(output).convert()

# Create DataMatrix images for each code
datamatrix_images = {code: create_datamatrix_image(code) for code in codes}

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.unicode.isdigit():
                key = f"KEY{int(event.unicode):02d}"
                if key in codes:
                    sounds[key].play()

    # Draw everything
    screen.fill(WHITE)
    for idx, code in enumerate(codes):
        datamatrix_image = datamatrix_images[code]
        x = (idx % COLUMNS) * (WIDTH // COLUMNS) + (WIDTH // COLUMNS - datamatrix_image.get_width()) // 2
        y = (idx // COLUMNS) * (HEIGHT // 4) + (HEIGHT // 4 - datamatrix_image.get_height()) // 2
        screen.blit(datamatrix_image, (x, y))

    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
