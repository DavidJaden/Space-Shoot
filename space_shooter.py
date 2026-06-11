import pygame
import sys
import random
import math
import numpy as np

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
GOLD = (255, 215, 0)
PINK = (255, 105, 180)
BLUE = (0, 100, 255)

# Player settings
player_width = 50
player_height = 40
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 7
player_base_speed = 7

# Bullet settings
bullets = []
bullet_speed = 7
bullet_width = 4
bullet_height = 10
double_bullet = False
double_bullet_timer = 0

# Shield power up state
shield_active = False
shield_timer = 0

# Speed boost power up state
speed_boost_active = False
speed_boost_timer = 0

# Power ups [x, y, type]
powerups = []
POWERUP_TYPES = {
    0: {"color": YELLOW, "label": "2x"},   # double bullet
    1: {"color": BLUE,   "label": "S"},    # shield
    2: {"color": PINK,   "label": ">>"},   # speed boost
}
first_boss_killed = False

# Enemy types
ENEMY_TYPES = {
    0: {"color": RED,    "speed": 2, "health": 1, "width": 40, "height": 30, "points": 10},  # standard
    1: {"color": CYAN,   "speed": 3, "health": 1, "width": 30, "height": 22, "points": 20},  # fast
    2: {"color": PURPLE, "speed": 1, "health": 3, "width": 50, "height": 38, "points": 30},  # tank
}

# Boss types
BOSS_TYPES = {
    0: {"name": "TANK",    "color": GOLD,   "health_mult": 2.0, "speed": 1.5, "shoots": False},
    1: {"name": "SPEEDER", "color": CYAN,   "health_mult": 0.8, "speed": 4.0, "shoots": False},
    2: {"name": "SHOOTER", "color": RED,    "health_mult": 1.2, "speed": 2.0, "shoots": True},
}

# Boss state
BOSS_WIDTH = 100
BOSS_HEIGHT = 80
BOSS_HEALTH_BASE = 15
bosses = []
boss_active = False
boss_direction = 1
boss_warning_timer = 0
BOSS_WARNING_DURATION = 180
boss_bullets = []
boss_shoot_timer = 0
dual_boss_unlocked = False

# Enemy spawn state
enemies = []
spawn_timer = 0
spawn_rate = 100

# Stars background
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

# Game state
score = 0
lives = 3
invincible = 0
difficulty = 1
highest_level = 1
paused = False

# Volume control, range 0.0 to 1.0, comma to lower and period to raise
master_volume = 0.5

# Dev console
dev_input = ""
dev_console_active = False

# Tracks which levels have already triggered a boss so pausing cant retrigger it
boss_levels_spawned = set()

# Level up display
level_up_timer = 0
LEVEL_UP_DURATION = 120

# Sound setup
pygame.mixer.init()

def generate_sound(frequency, duration, volume=0.3, wave_type='square'):
    # Generates audio samples as a numpy array at a given frequency and wave shape
    # Same numpy array approach used in the housing price prediction model,
    # just applied to audio data instead of housing data
    sample_rate = 44100
    samples = int(sample_rate * duration)
    buf = []
    for i in range(samples):
        t = i / sample_rate
        if wave_type == 'square':
            val = 1.0 if (frequency * t % 1) < 0.5 else -1.0
        elif wave_type == 'sine':
            val = math.sin(2 * math.pi * frequency * t)
        else:
            val = 0.0
        buf.append(int(val * volume * 32767))
    sound = pygame.sndarray.make_sound(
        np.array(buf, dtype='int16').reshape(-1, 1).repeat(2, axis=1)
    )
    return sound

def generate_music():
    # Loops through musical notes applying exponential decay to each
    # giving that spacey fading echo feel
    notes = [220, 247, 262, 294, 330, 294, 262, 247]
    sample_rate = 44100
    buf = []
    for note in notes:
        for i in range(int(sample_rate * 0.3)):
            t = i / sample_rate
            val = math.sin(2 * math.pi * note * t) * math.exp(-3 * t)
            buf.append(int(val * 0.15 * 32767))
    arr = np.array(buf, dtype='int16').reshape(-1, 1).repeat(2, axis=1)
    return pygame.sndarray.make_sound(arr)

# Generate all sounds upfront, shoot volume low so repeated firing isnt overwhelming
shoot_sound = generate_sound(880, 0.08, 0.07, 'square')
explosion_sound = generate_sound(120, 0.2, 0.3, 'square')
level_up_sound = generate_sound(660, 0.3, 0.2, 'sine')
boss_sound = generate_sound(110, 0.5, 0.4, 'square')
powerup_sound = generate_sound(440, 0.2, 0.3, 'sine')
music_sound = generate_music()
music_sound.play(-1)

def set_volume(vol):
    # Applies master volume to all sounds, music runs quieter than effects
    shoot_sound.set_volume(vol * 0.35)
    explosion_sound.set_volume(vol)
    level_up_sound.set_volume(vol)
    boss_sound.set_volume(vol)
    powerup_sound.set_volume(vol)
    music_sound.set_volume(vol * 0.5)

set_volume(master_volume)

# Fonts
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 32)
font_tiny = pygame.font.SysFont(None, 24)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
game_state = STATE_MENU


def get_bullet_damage():
    # Damage scales up every 5 levels so the player keeps up with harder enemies
    return 1 + (difficulty // 5)


def get_boss_weights():
    # Odds shift toward harder boss types as difficulty increases
    if difficulty >= 10:
        return [30, 30, 40]
    elif difficulty >= 7:
        return [40, 30, 30]
    else:
        return [60, 20, 20]


def spawn_boss():
    # Triggers boss warning and adds one or two bosses depending on difficulty
    # Dual bosses unlock at level 10
    global boss_active, boss_warning_timer, boss_shoot_timer
    boss_warning_timer = BOSS_WARNING_DURATION
    boss_active = True
    boss_shoot_timer = 0
    boss_sound.play()

    if difficulty >= 10:
        types = random.choices([0, 1, 2], weights=get_boss_weights(), k=2)
        for i, btype in enumerate(types):
            cfg = BOSS_TYPES[btype]
            health = int((BOSS_HEALTH_BASE + difficulty * 3) * cfg["health_mult"])
            bosses.append({
                "x": WIDTH // 4 * (i + 1) - BOSS_WIDTH // 2,
                "y": -BOSS_HEIGHT,
                "health": health,
                "max_health": health,
                "speed": cfg["speed"],
                "type": btype,
                "direction": 1 if i == 0 else -1,
                "entering": True,
                "shoot_timer": 0
            })
    else:
        btype = random.choices([0, 1, 2], weights=get_boss_weights())[0]
        cfg = BOSS_TYPES[btype]
        health = int((BOSS_HEALTH_BASE + difficulty * 3) * cfg["health_mult"])
        bosses.append({
            "x": WIDTH // 2 - BOSS_WIDTH // 2,
            "y": -BOSS_HEIGHT,
            "health": health,
            "max_health": health,
            "speed": cfg["speed"],
            "type": btype,
            "direction": 1,
            "entering": True,
            "shoot_timer": 0
        })


def drop_powerup(x, y):
    # Drops a random power up at the boss kill position
    # Only active after the first boss has been defeated
    if not first_boss_killed:
        return
    ptype = random.randint(0, 2)
    powerups.append([x, y, ptype])


def reset_game():
    # Resets all game state back to starting values
    # Score starts at the beginning of the highest level reached for the continue feature
    global player_x, player_y, bullets, enemies, spawn_timer, score
    global lives, invincible, difficulty, stars, level_up_timer
    global bosses, boss_active, boss_direction, boss_warning_timer
    global boss_bullets, boss_shoot_timer, powerups
    global double_bullet, double_bullet_timer, shield_active, shield_timer
    global speed_boost_active, speed_boost_timer, player_speed, first_boss_killed
    global paused, boss_levels_spawned, dev_input, dev_console_active
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    bullets = []
    enemies = []
    spawn_timer = 0
    score = (highest_level - 1) * 150
    lives = 3
    invincible = 0
    difficulty = highest_level
    level_up_timer = 0
    bosses = []
    boss_active = False
    boss_direction = 1
    boss_warning_timer = 0
    boss_bullets = []
    boss_shoot_timer = 0
    powerups = []
    double_bullet = False
    double_bullet_timer = 0
    shield_active = False
    shield_timer = 0
    speed_boost_active = False
    speed_boost_timer = 0
    player_speed = player_base_speed
    first_boss_killed = False
    paused = False
    boss_levels_spawned = set()
    dev_input = ""
    dev_console_active = False
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]


def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)


def update_stars():
    # Stars scroll downward and wrap back to top, speed increases with difficulty
    global stars
    stars = [(x, (y + difficulty) % HEIGHT) for x, y in stars]


def draw_player(x, y):
    # Triangle ship with wings and orange engine glow
    # Turns cyan while invincible, shows blue shield ring when shield is active
    if shield_active:
        pygame.draw.circle(screen, BLUE,
            (x + player_width // 2, y + player_height // 2),
            player_width, 2)
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
    # Player bullets yellow, boss bullets red
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW,
            (bullet[0], bullet[1], bullet_width, bullet_height))
    for bullet in boss_bullets:
        pygame.draw.rect(screen, RED,
            (bullet[0], bullet[1], 6, 12))


def draw_enemies():
    # Each enemy is a downward pointing triangle in its type color
    for enemy in enemies:
        ex, ey, etype, _ = enemy
        cfg = ENEMY_TYPES[etype]
        ew, eh = cfg["width"], cfg["height"]
        pygame.draw.polygon(screen, cfg["color"], [
            (ex + ew // 2, ey + eh),
            (ex, ey),
            (ex + ew, ey)
        ])


def draw_bosses():
    # Handles warning flash then draws boss with health bar
    if not boss_active:
        return

    if boss_warning_timer > 0:
        if (boss_warning_timer // 15) % 2 == 0:
            warning = font_medium.render("WARNING -- BOSS INCOMING", True, RED)
            screen.blit(warning, (WIDTH // 2 - warning.get_width() // 2, HEIGHT // 2 - 20))
        return

    for idx, boss in enumerate(bosses):
        bx, by = int(boss["x"]), int(boss["y"])
        cfg = BOSS_TYPES[boss["type"]]

        # Main body
        pygame.draw.polygon(screen, cfg["color"], [
            (bx + BOSS_WIDTH // 2, by),
            (bx, by + BOSS_HEIGHT),
            (bx + BOSS_WIDTH, by + BOSS_HEIGHT)
        ])
        # Left wing
        pygame.draw.polygon(screen, ORANGE, [
            (bx - 20, by + BOSS_HEIGHT),
            (bx, by + BOSS_HEIGHT // 2),
            (bx, by + BOSS_HEIGHT)
        ])
        # Right wing
        pygame.draw.polygon(screen, ORANGE, [
            (bx + BOSS_WIDTH + 20, by + BOSS_HEIGHT),
            (bx + BOSS_WIDTH, by + BOSS_HEIGHT // 2),
            (bx + BOSS_WIDTH, by + BOSS_HEIGHT)
        ])
        # Eye
        pygame.draw.circle(screen, RED, (bx + BOSS_WIDTH // 2, by + BOSS_HEIGHT // 2), 8)

        name_surf = font_tiny.render(cfg["name"], True, WHITE)
        screen.blit(name_surf, (bx + BOSS_WIDTH // 2 - name_surf.get_width() // 2, by - 20))

        # Health bar
        bar_width = 200 if len(bosses) > 1 else 300
        bar_x = (WIDTH // 4 * (idx + 1) - bar_width // 2) if len(bosses) > 1 else WIDTH // 2 - bar_width // 2
        bar_y = 15
        health_pct = boss["health"] / boss["max_health"]
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, 15))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * health_pct), 15))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, 15), 2)
        label = font_tiny.render(f"BOSS {idx + 1}: {cfg['name']}", True, GOLD)
        screen.blit(label, (bar_x + bar_width // 2 - label.get_width() // 2, bar_y + 18))


def draw_powerups():
    # Colored circles with labels falling down the screen
    for pu in powerups:
        px, py, ptype = pu
        cfg = POWERUP_TYPES[ptype]
        pygame.draw.circle(screen, cfg["color"], (px, py), 15)
        label = font_tiny.render(cfg["label"], True, BLACK)
        screen.blit(label, (px - label.get_width() // 2, py - label.get_height() // 2))


def draw_pause():
    # Semi transparent overlay keeps the game visible behind the pause screen
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))
    pause_text = font_large.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
    resume_text = font_small.render("Press ESC to Resume", True, YELLOW)
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 20))
    menu_text = font_small.render("Press Q to Quit to Menu", True, (180, 180, 180))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 55))
    vol_text = font_tiny.render(f"Volume: {int(master_volume * 100)}%  (< to lower  > to raise)", True, (140, 140, 140))
    screen.blit(vol_text, (WIDTH // 2 - vol_text.get_width() // 2, HEIGHT // 2 + 90))


def draw_dev_console():
    # Faint hint in bottom right when closed, input box when open
    if not dev_console_active:
        hint = font_tiny.render("~ for dev console", True, (60, 60, 60))
        screen.blit(hint, (WIDTH - hint.get_width() - 10, HEIGHT - 20))
        return
    pygame.draw.rect(screen, (20, 20, 20), (WIDTH - 220, HEIGHT - 35, 210, 28))
    pygame.draw.rect(screen, YELLOW, (WIDTH - 220, HEIGHT - 35, 210, 28), 1)
    label = font_tiny.render(f"Code: {dev_input}_", True, YELLOW)
    screen.blit(label, (WIDTH - 215, HEIGHT - 30))


def update_bosses():
    # Boss movement, shooting, bullet collision, and player collision all handled here
    # Boss enters from the top then moves side to side once in position
    # Shooter type fires downward at an interval that decreases with difficulty
    global boss_active, boss_warning_timer, lives, invincible
    global game_state, score, first_boss_killed, boss_bullets
    global shield_active, shield_timer

    if not boss_active:
        return

    if boss_warning_timer > 0:
        boss_warning_timer -= 1
        if boss_warning_timer == 0:
            for b in bosses:
                b["entering"] = False
        return

    bullets_used = set()

    for boss in bosses[:]:
        # Slide into position before starting side to side movement
        if boss["y"] < 60:
            boss["y"] += boss["speed"]
            continue

        boss["x"] += boss["speed"] * boss["direction"]
        if boss["x"] <= 0 or boss["x"] >= WIDTH - BOSS_WIDTH:
            boss["direction"] *= -1

        # Shooter boss fires downward bullets
        cfg = BOSS_TYPES[boss["type"]]
        if cfg["shoots"]:
            boss["shoot_timer"] += 1
            shoot_interval = max(30, 90 - difficulty * 5)
            if boss["shoot_timer"] >= shoot_interval:
                boss_bullets.append([int(boss["x"]) + BOSS_WIDTH // 2, int(boss["y"]) + BOSS_HEIGHT])
                boss["shoot_timer"] = 0

        # Player bullet hits boss
        for i, bullet in enumerate(bullets):
            if i in bullets_used:
                continue
            bx, by = int(boss["x"]), int(boss["y"])
            if (bullet[0] > bx and bullet[0] < bx + BOSS_WIDTH and
                    bullet[1] > by and bullet[1] < by + BOSS_HEIGHT):
                bullets_used.add(i)
                boss["health"] -= get_bullet_damage()
                if boss["health"] <= 0:
                    score += 50
                    explosion_sound.play()
                    drop_powerup(int(boss["x"]) + BOSS_WIDTH // 2, int(boss["y"]) + BOSS_HEIGHT // 2)
                    if not first_boss_killed:
                        first_boss_killed = True
                    bosses.remove(boss)
                    break

        # Boss body hits player, shield absorbs one hit otherwise lose a life
        bx, by = int(boss["x"]), int(boss["y"])
        if (player_x < bx + BOSS_WIDTH and player_x + player_width > bx and
                player_y < by + BOSS_HEIGHT and player_y + player_height > by):
            if invincible == 0:
                if shield_active:
                    shield_active = False
                    shield_timer = 0
                else:
                    lives -= 1
                    invincible = 90
                    if lives <= 0:
                        game_state = STATE_GAME_OVER

    bullets[:] = [b for i, b in enumerate(bullets) if i not in bullets_used]

    # Clear boss state once all bosses are defeated
    if len(bosses) == 0:
        boss_active = False
        boss_bullets = []

    # Boss bullets move down and check against player position, shield absorbs one hit
    for bullet in boss_bullets[:]:
        bullet[1] += 5
        if (bullet[0] > player_x and bullet[0] < player_x + player_width and
                bullet[1] > player_y and bullet[1] < player_y + player_height):
            if invincible == 0:
                if shield_active:
                    shield_active = False
                    shield_timer = 0
                else:
                    lives -= 1
                    invincible = 90
                    if lives <= 0:
                        game_state = STATE_GAME_OVER
            boss_bullets.remove(bullet)

    boss_bullets[:] = [b for b in boss_bullets if b[1] < HEIGHT]


def update_powerups():
    # Power ups fall downward like enemies
    # Player flies into them or shoots them to collect
    # Reuses the same collision detection approach as enemy hits
    # Timers count down and deactivate the effect when they expire
    global double_bullet, double_bullet_timer, shield_active, shield_timer
    global speed_boost_active, speed_boost_timer, player_speed

    for pu in powerups[:]:
        pu[1] += 2  # fall downward
        px, py, ptype = pu

        collected = False

        # Player flies into it
        if (player_x < px + 15 and player_x + player_width > px - 15 and
                player_y < py + 15 and player_y + player_height > py - 15):
            collected = True

        # Player shoots it
        if not collected:
            for bullet in bullets[:]:
                if (bullet[0] > px - 15 and bullet[0] < px + 15 and
                        bullet[1] > py - 15 and bullet[1] < py + 15):
                    bullets.remove(bullet)
                    collected = True
                    break

        if collected:
            powerup_sound.play()
            if ptype == 0:
                double_bullet = True
                double_bullet_timer = 300
            elif ptype == 1:
                shield_active = True
                shield_timer = 300
            elif ptype == 2:
                speed_boost_active = True
                speed_boost_timer = 300
                player_speed = player_base_speed + 4
            powerups.remove(pu)
        elif py > HEIGHT:
            powerups.remove(pu)

    if double_bullet_timer > 0:
        double_bullet_timer -= 1
        if double_bullet_timer == 0:
            double_bullet = False

    if shield_timer > 0:
        shield_timer -= 1
        if shield_timer == 0:
            shield_active = False

    if speed_boost_timer > 0:
        speed_boost_timer -= 1
        if speed_boost_timer == 0:
            speed_boost_active = False
            player_speed = player_base_speed


def draw_hud():
    # Score, lives, level top left, active power up timers top right
    # Damage indicator only shows when above base value
    screen.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font_small.render(f"Lives: {lives}", True, GREEN), (10, 40))
    screen.blit(font_small.render(f"Level: {difficulty}", True, YELLOW), (10, 70))

    x_offset = WIDTH - 150
    if double_bullet:
        surf = font_tiny.render(f"2x BULLET: {double_bullet_timer // 60 + 1}s", True, YELLOW)
        screen.blit(surf, (x_offset, 10))
    if shield_active:
        surf = font_tiny.render(f"SHIELD: {shield_timer // 60 + 1}s", True, BLUE)
        screen.blit(surf, (x_offset, 30))
    if speed_boost_active:
        surf = font_tiny.render(f"SPEED: {speed_boost_timer // 60 + 1}s", True, PINK)
        screen.blit(surf, (x_offset, 50))

    dmg = get_bullet_damage()
    if dmg > 1:
        surf = font_tiny.render(f"DMG: {dmg}", True, ORANGE)
        screen.blit(surf, (10, 100))

    # Volume indicator in bottom left
    vol_surf = font_tiny.render(f"VOL: {int(master_volume * 100)}%", True, (100, 100, 100))
    screen.blit(vol_surf, (10, HEIGHT - 20))


def draw_level_up():
    # Fades the level up message out over time using alpha
    if level_up_timer > 0:
        alpha = min(255, level_up_timer * 3)
        surf = font_medium.render(f"LEVEL UP! Level {difficulty}", True, YELLOW)
        surf.set_alpha(alpha)
        screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - 30))


def draw_menu():
    # Two column layout, enemy types left and power ups right
    screen.fill(BLACK)
    draw_stars()
    title = font_large.render("SPACE SHOOTER", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    start_text = font_medium.render("Press ENTER to Start", True, YELLOW)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 200))
    quit_text = font_small.render("Press Q to Quit", True, (180, 180, 180))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 250))

    col1_x = 80
    col2_x = WIDTH // 2 + 40
    row_y = 310

    enemy_title = font_small.render("Enemy Types:", True, WHITE)
    screen.blit(enemy_title, (col1_x, row_y))
    types = [
        (RED,    "Standard -- 1 HP"),
        (CYAN,   "Fast -- 1 HP"),
        (PURPLE, "Tank -- 3 HP"),
        (GOLD,   "Boss -- every 5 levels"),
    ]
    for i, (color, label) in enumerate(types):
        surf = font_tiny.render(label, True, color)
        screen.blit(surf, (col1_x, row_y + 28 + i * 22))

    powerup_title = font_small.render("Power Ups:", True, WHITE)
    screen.blit(powerup_title, (col2_x, row_y))
    pu_types = [
        (YELLOW, "2x -- Double bullets"),
        (BLUE,   "S  -- Shield"),
        (PINK,   ">> -- Speed boost"),
        (WHITE,  "Drop on boss kill, catch them"),
    ]
    for i, (color, label) in enumerate(pu_types):
        surf = font_tiny.render(label, True, color)
        screen.blit(surf, (col2_x, row_y + 28 + i * 22))

    pygame.display.flip()


def draw_game_over():
    # Final score, level reached, continue or restart options
    screen.fill(BLACK)
    draw_stars()
    over_text = font_large.render("GAME OVER", True, RED)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 150))
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 250))
    level_text = font_small.render(f"Level Reached: {difficulty}", True, YELLOW)
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 310))
    continue_text = font_small.render(f"Continue from Level {highest_level}?", True, CYAN)
    screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, 350))
    restart_text = font_small.render("ENTER to Continue  |  R to Restart  |  Q to Quit", True, YELLOW)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 400))
    pygame.display.flip()


# Main game loop
while True:

    # Menu state
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

    # Game over state
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
                if event.key == pygame.K_r:
                    highest_level = 1
                    reset_game()
                    game_state = STATE_PLAYING
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)
        continue

    # Playing state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # ESC toggles pause unless dev console is open
            if event.key == pygame.K_ESCAPE and not dev_console_active:
                paused = not paused
            # Backtick opens and closes the dev console
            elif event.key == pygame.K_BACKQUOTE:
                dev_console_active = not dev_console_active
                dev_input = ""
            # Volume controls, comma to lower and period to raise
            elif event.key == pygame.K_COMMA and not dev_console_active:
                master_volume = max(0.0, master_volume - 0.1)
                set_volume(master_volume)
            elif event.key == pygame.K_PERIOD and not dev_console_active:
                master_volume = min(1.0, master_volume + 0.1)
                set_volume(master_volume)
            elif dev_console_active:
                if event.key == pygame.K_RETURN:
                    if dev_input.startswith("Jab") and dev_input[3:].isdigit():
                        target_level = int(dev_input[3:])
                        if target_level >= 1:
                            score = (target_level - 1) * 150
                            difficulty = target_level
                            highest_level = max(highest_level, target_level)
                            enemies = []
                            boss_bullets = []
                            bosses = []
                            boss_active = False
                            first_boss_killed = True
                            # If jumping to a boss level spawn it immediately
                            if target_level % 5 == 0:
                                boss_levels_spawned.add(target_level)
                                spawn_boss()
                            else:
                                boss_levels_spawned.discard(target_level)
                    dev_input = ""
                    dev_console_active = False
                elif event.key == pygame.K_BACKSPACE:
                    dev_input = dev_input[:-1]
                else:
                    if len(dev_input) < 10:
                        dev_input += event.unicode
            if not paused and not dev_console_active:
                if event.key == pygame.K_SPACE:
                    # Double bullet fires two side by side shots
                    if double_bullet:
                        bullets.append([player_x + player_width // 2 - 8, player_y])
                        bullets.append([player_x + player_width // 2 + 8, player_y])
                    else:
                        bullets.append([player_x + player_width // 2, player_y])
                    shoot_sound.play()
            if paused and not dev_console_active:
                if event.key == pygame.K_q:
                    game_state = STATE_MENU

    # Freeze all logic while paused
    if paused:
        draw_pause()
        pygame.display.flip()
        clock.tick(FPS)
        continue

    screen.fill(BLACK)
    update_stars()
    draw_stars()

    # Player movement clamped to screen bounds
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    # Move bullets up and remove off screen ones
    for bullet in bullets:
        bullet[1] -= bullet_speed
    bullets = [b for b in bullets if b[1] > 0]

    # Level increases every 150 points, boss spawns at every 5th level once per level
    new_difficulty = 1 + score // 150
    if new_difficulty > difficulty:
        difficulty = new_difficulty
        if difficulty > highest_level:
            highest_level = difficulty
        level_up_timer = LEVEL_UP_DURATION
        level_up_sound.play()
        if difficulty % 5 == 0 and not boss_active and difficulty not in boss_levels_spawned:
            boss_levels_spawned.add(difficulty)
            spawn_boss()
            enemies = []

    if level_up_timer > 0:
        level_up_timer -= 1

    # Spawn rate and speed scale with difficulty, speed capped at 4.0
    current_spawn_rate = max(25, spawn_rate - (difficulty * 5))
    current_speed_boost = min((difficulty - 1) * 0.3, 4.0)

    # Regular enemy logic only runs when no boss is active
    if not boss_active:
        spawn_timer += 1
        if spawn_timer >= current_spawn_rate:
            etype = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
            cfg = ENEMY_TYPES[etype]
            # Edge buffer narrows as difficulty increases to keep spawns manageable
            # Prevents fast enemies from appearing in corners the player cant reach in time
            edge_buffer = min(120 + (difficulty * 10), WIDTH // 3)
            ex = random.randint(edge_buffer, WIDTH - cfg["width"] - edge_buffer)
            enemies.append([ex, -cfg["height"], etype, cfg["health"]])
            spawn_timer = 0

        # Move enemies down
        for enemy in enemies:
            enemy[1] += ENEMY_TYPES[enemy[2]]["speed"] + current_speed_boost

        # Enemies that pass the bottom cost a life
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

        # Bullet vs enemy, track indices to avoid modifying list mid loop
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
                    enemy[3] -= get_bullet_damage()
                    if enemy[3] <= 0:
                        enemies_to_remove.append(j)
                        score += cfg["points"]
                        explosion_sound.play()

        bullets = [b for i, b in enumerate(bullets) if i not in bullets_to_remove]
        enemies = [e for j, e in enumerate(enemies) if j not in enemies_to_remove]

        invincible = max(0, invincible - 1)

        # Player vs enemy, shield absorbs one hit otherwise lose a life
        for enemy in enemies:
            ex, ey, etype, health = enemy
            cfg = ENEMY_TYPES[etype]
            ew, eh = cfg["width"], cfg["height"]
            if (player_x < ex + ew and player_x + player_width > ex and
                    player_y < ey + eh and player_y + player_height > ey):
                if invincible == 0:
                    if shield_active:
                        shield_active = False
                        shield_timer = 0
                    else:
                        lives -= 1
                        invincible = 90
                        if lives <= 0:
                            game_state = STATE_GAME_OVER

    invincible = max(0, invincible - 1)
    update_bosses()
    update_powerups()

    # Player blinks while invincible using frame based alternation
    if invincible == 0 or (invincible // 5) % 2 == 0:
        draw_player(player_x, player_y)

    draw_bullets()
    draw_enemies()
    draw_bosses()
    draw_powerups()
    draw_hud()
    draw_level_up()
    draw_dev_console()

    pygame.display.flip()
    clock.tick(FPS)