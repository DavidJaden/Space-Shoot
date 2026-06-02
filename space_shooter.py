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
GREEN = (0, 255, 0)

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

# Enemy types
ENEMY_TYPES = {
    0: {"color": RED,    "speed": 2, "health": 1, "width": 40, "height": 30, "points": 10},
    1: {"color": CYAN,   "speed": 4, "health": 1, "width": 30, "height": 22, "points": 20},
    2: {"color": PURPLE, "speed": 1, "health": 3, "width": 50, "height": 38, "points": 30},
}

enemies = []
spawn_timer = 0
spawn_rate = 90

# Stars
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

# Game state
score = 0
lives = 3
invincible = 0
difficulty = 1

# Fonts
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 32)

# Clock
clock = pygame.time.Clock()
FPS = 60

# States
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
game_state = STATE_MENU


def reset_game():
    global player_x, player_y, bullets, enemies, spawn_timer, score, lives, invincible, difficulty, stars
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    bullets = []
    enemies = []
    spawn_timer = 0
    score = 0
    lives = 3
    invincible = 0
    difficulty = 1
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]


def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)


def update_stars():
    global stars
    stars = [(x, (y + difficulty) % HEIGHT) for x, y in stars]


def draw_player(x, y):
    col = (0, 200, 255) if invincible > 0 else WHITE
    pygame.draw.polygon(screen, col, [
        (x + player_width // 2, y),
        (x + 5, y + player_height),
        (x + player_width - 5, y + player_height)
    ])
    pygame.draw.polygon(screen, col, [
        (x, y + player_height),
        (x + 15, y + player_height - 10),
        (x + 15, y + player_height)
    ])
    pygame.draw.polygon(screen, col, [
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
    screen.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font_small.render(f"Lives: {lives}", True, GREEN), (10, 40))
    screen.blit(font_small.render(f"Level: {difficulty}", True, YELLOW), (10, 70))


def draw_menu():
    screen.fill(BLACK)
    draw_stars()
    title = font_large.render("SPACE SHOOTER", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
    start_text = font_medium.render("Press ENTER to Start", True, YELLOW)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 300))
    quit_text = font_small.render("Press Q to Quit", True, (180, 180, 180))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 370))
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


def draw_game_over():
    screen.fill(BLACK)
    draw_stars()
    over_text = font_large.render("GAME OVER", True, RED)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 180))
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 280))
    level_text = font_small.render(f"Level Reached: {difficulty}", True, YELLOW)
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 330))
    restart_text = font_small.render("Press ENTER to Play Again  |  Q to Quit", True, YELLOW)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 390))
    pygame.display.flip()


# Main game loop
while True:

    if game_state == STATE_MENU:
        update_stars()
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

    if game_state == STATE_GAME_OVER:
        update_stars()
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

    # PLAYING
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
    update_stars()
    draw_stars()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    for bullet in bullets:
        bullet[1] -= bullet_speed
    bullets = [b for b in bullets if b[1] > 0]

    # Difficulty scaling
    difficulty = 1 + score // 100
    current_spawn_rate = max(20, spawn_rate - (difficulty * 5))
    current_speed_boost = difficulty * 0.5

    spawn_timer += 1
    if spawn_timer >= current_spawn_rate:
        etype = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
        cfg = ENEMY_TYPES[etype]
        ex = random.randint(0, WIDTH - cfg["width"])
        enemies.append([ex, -cfg["height"], etype, cfg["health"]])
        spawn_timer = 0

    # Move enemies with difficulty speed boost
    for enemy in enemies:
        enemy[1] += ENEMY_TYPES[enemy[2]]["speed"] + current_speed_boost
    
    # Enemies passing bottom lose a life
    surviving = []
    for e in enemies:
        if e[1] < HEIGHT:
            surviving.append(e)
        else:
            if invincible == 0:
                lives -= 1
                invincible = 90
                if lives <= 0:
                    game_state = STATE_GAME_OVER
    enemies = surviving

    # Bullet vs enemy collision
    bullets_to_remove = []
    enemies_to_remove = []

    for i, bullet in enumerate(bullets):
        for j, enemy in enumerate(enemies):
            cfg = ENEMY_TYPES[enemy[2]]
            ex, ey, etype, health = enemy
            ew, eh = cfg["width"], cfg["height"]
            if (bullet[0] > ex and bullet[0] < ex + ew and
                    bullet[1] > ey and bullet[1] < ey + eh):
                bullets_to_remove.append(i)
                enemy[3] -= 1
                if enemy[3] <= 0:
                    enemies_to_remove.append(j)
                    score += cfg["points"]

    bullets = [b for i, b in enumerate(bullets) if i not in bullets_to_remove]
    enemies = [e for j, e in enumerate(enemies) if j not in enemies_to_remove]

    # Player vs enemy collision
    invincible = max(0, invincible - 1)
    for enemy in enemies:
        ex, ey, etype, health = enemy
        cfg = ENEMY_TYPES[etype]
        ew, eh = cfg["width"], cfg["height"]
        if (player_x < ex + ew and player_x + player_width > ex and
                player_y < ey + eh and player_y + player_height > ey):
            if invincible == 0:
                lives -= 1
                invincible = 90
                if lives <= 0:
                    game_state = STATE_GAME_OVER

    if invincible == 0 or (invincible // 5) % 2 == 0:
        draw_player(player_x, player_y)

    draw_bullets()
    draw_enemies()
    draw_hud()

    pygame.display.flip()
    clock.tick(FPS)