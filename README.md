# Space Shooter
A 2D space shooter game built with Python and Pygame as part of the SEO Tech Developer Fellowship.

## Features
- Three enemy types: Standard, Fast, and Tank with varying speed and health
- Three boss types: Tank, Speeder, and Shooter - spawns every 5 levels with increasing difficulty
- Dual boss encounters unlocked at level 10+
- Power up system - double bullets, shield, and speed boost drop after first boss kill
- Bullet damage scaling - damage increases every 5 levels
- Difficulty scaling - enemies spawn faster and move quicker as score increases
- Enemy speed capped to prevent impossible difficulty at high levels
- Lives system with invincibility frames
- Continue from last level reached on game over
- Collision detection for bullets, enemies, bosses, and boss bullets
- Scrolling star background that speeds up with difficulty
- Level up notification with fading on screen message
- Pause system with overlay screen
- Dev console for level skipping
- Procedurally generated sound effects and background music
- Two column main menu with enemy and power up legend
- Game over screen showing score and level reached

## How to Run
1. Make sure Python is installed
2. Install dependencies: `pip3 install pygame numpy`
3. Clone the repo: `git clone https://github.com/DavidJaden/Space-Shoot.git`
4. Run: `python3 space_shooter.py`

## Controls
- Left / Right arrow keys - move ship
- Spacebar - shoot
- Escape - pause game
- Q - quit to menu while paused
- Backtick (~) - open dev console
- R on game over - restart from level 1
- Enter on game over - continue from highest level reached

## Dev Console
Press backtick to open. Type Jab followed by a number to skip to any level.
Example: Jab10 skips to level 10, Jab5 skips to level 5.

## Built With
- Python
- Pygame
- Numpy
- Git

## Authors
- Jaden David
- Abdullah Ratol
