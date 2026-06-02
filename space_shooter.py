import pygame
import sys
import random

pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 100, 0)
CYAN = (0, 255, 255)
PURPLE = (180, 0, 255)

# Player settings
player_width = 50
player_height = 40
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 5

# Bullet settings
bullets = []
bullet_speed = 7
bullet_width = 4
bullet_height = 10

# Enemy settings
# Each enemy: [x, y, type]
# type 0 = standard (red,    speed 2, health 1)
# type 1 = fast     (cyan,   speed 4, health 1)
# type 2 = tank     (purple, speed 1, health 3)
enemies = []

ENEMY_TYPES = {
    0: {"color": RED,    "speed": 2, "health": 1, "width": 40, "height": 30, "points": 10},
    1: {"color": CYAN,   "speed": 4, "health": 1, "width": 30, "height": 22, "points": 20},
    2: {"color": PURPLE, "speed": 1, "health": 3, "width": 50, "height": 38, "points": 30},
}

spawn_timer = 0
spawn_rate = 60

# Score
score = 0
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 32)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
game_state = STATE_MENU


#  Drawing helpers

def draw_player(x, y):
    pygame.draw.polygon(screen, WHITE, [
        (x + player_width // 2, y),
        (x + 5, y + player_height),
        (x + player_width - 5, y + player_height)
    ])
    pygame.draw.polygon(screen, WHITE, [
        (x, y + player_height),
        (x + 15, y + player_height - 10),
        (x + 15, y + player_height)
    ])
    pygame.draw.polygon(screen, WHITE, [
        (x + player_width, y + player_height),
        (x + player_width - 15, y + player_height - 10),
        (x + player_width - 15, y + player_height)
    ])
    pygame.draw.rect(screen, ORANGE,
        (x + player_width // 2 - 5, y + player_height, 10, 8))


def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW,
            (bullet[0], bullet[1], bullet_width, bullet_height))


def draw_enemies():
    for enemy in enemies:
        ex, ey, etype, _ = enemy
        cfg = ENEMY_TYPES[etype]
        ew, eh = cfg["width"], cfg["height"]
        pygame.draw.polygon(screen, cfg["color"], [
            (ex + ew // 2, ey + eh),
            (ex, ey),
            (ex + ew, ey)
        ])


def draw_hud():
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (10, 10))


#  Main menu

def draw_menu():
    screen.fill(BLACK)

    title = font_large.render("SPACE SHOOTER", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

    start_text = font_medium.render("Press ENTER to Start", True, YELLOW)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 300))

    quit_text = font_small.render("Press Q to Quit", True, (180, 180, 180))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 370))

    # Enemy type legend
    legend_title = font_small.render("Enemy Types:", True, WHITE)
    screen.blit(legend_title, (WIDTH // 2 - 120, 450))

    types = [
        (RED,    "Standard  — normal speed, 1 HP"),
        (CYAN,   "Fast      — double speed, 1 HP"),
        (PURPLE, "Tank      — slow, 3 HP"),
    ]
    for i, (color, label) in enumerate(types):
        surf = font_small.render(label, True, color)
        screen.blit(surf, (WIDTH // 2 - 120, 480 + i * 28))

    pygame.display.flip()


#  Game over screen 

def draw_game_over():
    screen.fill(BLACK)

    over_text = font_large.render("GAME OVER", True, RED)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 180))

    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 280))

    restart_text = font_small.render("Press ENTER to Play Again  |  Q to Quit", True, YELLOW)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 360))

    pygame.display.flip()


# Reset game 

def reset_game():
    global player_x, player_y, bullets, enemies, spawn_timer, score
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    bullets = []
    enemies = []
    spawn_timer = 0
    score = 0


#  Main game loop.

while True:

    #  MENU 
    if game_state == STATE_MENU:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = STATE_PLAYING
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)
        continue

    # GAME OVER 
    if game_state == STATE_GAME_OVER:
        draw_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = STATE_PLAYING
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)
        continue

    # --- PLAYING --- 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append([player_x + player_width // 2, player_y])
            if event.key == pygame.K_ESCAPE:
                game_state = STATE_MENU

    screen.fill(BLACK)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    # Move bullets
    for bullet in bullets:
        bullet[1] -= bullet_speed
    bullets = [b for b in bullets if b[1] > 0]

    # Spawn enemies, weighted random type selection (i consulted claude for this section, will come back to re do eventually)
    spawn_timer += 1
    if spawn_timer >= spawn_rate:
        etype = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
        cfg = ENEMY_TYPES[etype]
        ex = random.randint(0, WIDTH - cfg["width"])
        # enemy list: [x, y, type, current_health]
        enemies.append([ex, -cfg["height"], etype, cfg["health"]])
        spawn_timer = 0

    # Move enemies
    for enemy in enemies:
        enemy[1] += ENEMY_TYPES[enemy[2]]["speed"]
    enemies = [e for e in enemies if e[1] < HEIGHT]

    # ── COLLISION ─────────────────────────────────────────────────────────────




    # bullet vs enemy collision goes here
    # player vs enemy collision (trigger game_over) goes here




    # Draw everything
    draw_bullets()
    draw_enemies()
    draw_player(player_x, player_y)
    draw_hud()

    pygame.display.flip()
    clock.tick(FPS)