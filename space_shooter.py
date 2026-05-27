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
enemies = []
enemy_width = 40
enemy_height = 30
enemy_speed = 2
spawn_timer = 0
spawn_rate = 60

# Clock
clock = pygame.time.Clock()
FPS = 60

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
    pygame.draw.rect(screen, (255, 100, 0),
        (x + player_width // 2 - 5, y + player_height, 10, 8))

def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 0),
            (bullet[0], bullet[1], bullet_width, bullet_height))

def draw_enemies():
    for enemy in enemies:
        pygame.draw.polygon(screen, (255, 0, 0), [
            (enemy[0] + enemy_width // 2, enemy[1] + enemy_height),
            (enemy[0], enemy[1]),
            (enemy[0] + enemy_width, enemy[1])
        ])

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append([player_x + player_width // 2, player_y])

    screen.fill(BLACK)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    for bullet in bullets:
        bullet[1] -= bullet_speed
    bullets = [b for b in bullets if b[1] > 0]

    spawn_timer += 1
    if spawn_timer >= spawn_rate:
        enemies.append([random.randint(0, WIDTH - enemy_width), -enemy_height])
        spawn_timer = 0

    for enemy in enemies:
        enemy[1] += enemy_speed
    enemies = [e for e in enemies if e[1] < HEIGHT]

    draw_bullets()
    draw_enemies()
    draw_player(player_x, player_y)

    pygame.display.flip()
    clock.tick(FPS)