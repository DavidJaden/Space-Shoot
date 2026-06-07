# Space Shooter — Patch Notes

---

## Version 0.5 — June 2026

### New Features
- Bullet damage now scales with level — increases by 1 every 5 levels
- Damage indicator shown in HUD when above base level
- Added dev console — press backtick to open, type Jab followed by a number to skip to any level instantly
- Jumping via dev console automatically unlocks power up drops

### Balance Changes
- Fixed score explosion bug after dual boss kills — boss kill now awards flat 50 points
- Boss health formula reworked to linear scaling — significantly more reasonable at high levels
- Enemy speed boost capped at 4.0 maximum
- Pause no longer resets boss state or allows bypass of boss levels
- Boss levels tracked in a set to prevent duplicate spawns on unpause

### Bug Fixes
- Fixed pause bypass exploit where ESC could skip boss encounters
- Fixed dual boss kill causing immediate jump to level 20+ due to uncapped score reward

---

## Version 0.4 — June 2026

### New Features
- Added procedurally generated sound effects using pygame mixer and numpy
- Added ambient background music that loops continuously during gameplay
- Added level up notification message that fades in on screen
- Added continue from last level feature on game over
- Added proper pause screen with semi transparent overlay
- Added three boss types — Tank, Speeder, Shooter with unique behavior
- Shooter boss fires bullets downward at player
- Dual boss spawn unlocked at level 10+
- Boss weights shift toward harder types as difficulty increases
- Three power ups drop after first boss kill — double bullet, shield, speed boost
- Power up timers shown in HUD
- Shield absorbs one hit from any source including boss bullets
- Corner spawn fix — enemies spawn in middle 60% of screen width
- Bottom of screen only costs life if enemy passes through middle 60%
- Two column main menu layout

### Balance Changes
- Player speed increased from 5 to 7
- Fast enemy speed reduced from 4 to 3
- Base spawn rate increased from 90 to 100 frames
- Level scaling triggers every 150 points
- Speed boost per level reduced from 0.5 to 0.3

### Bug Fixes
- Fixed global variable declaration error causing SyntaxError on restart
- Fixed merge conflict between collaborators causing collision detection to be missing

---

## Version 0.3 — June 2026

### New Features
- Added lives lost when enemies pass the bottom of the screen
- Added scrolling star background that speeds up with difficulty
- Added difficulty scaling
- Added level display to HUD
- Added game over screen showing score and level reached

### Balance Changes
- Spawn rate reduced from 60 to 90 frames between spawns

---

## Version 0.2 — June 2026

### New Features
- Added three distinct enemy types with unique colors speeds and health
- Added weighted random enemy spawning
- Added main menu screen with enemy type legend
- Added full collision detection for bullets and player
- Added lives system with invincibility frames
- Added score tracking with points per enemy type
- Added HUD displaying score and lives

---

## Version 0.1 — June 2026

### Initial Release
- Basic player movement with left and right arrow keys
- Spacebar shooting mechanic
- Basic enemy spawning and downward movement
- Black game window with white player ship and orange engine glow
- Quit and exit functionality
