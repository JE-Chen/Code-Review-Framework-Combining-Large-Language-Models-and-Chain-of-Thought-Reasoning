## PR Summary Template

### Summary Rules
#### Key Changes
- Added a new Python script `game.py` implementing a simple Pygame game with basic movement, collision detection, and scoring.

#### Impact Scope
- The script affects the entire application as it introduces a new gameplay module.

#### Purpose of Changes
- To create a functional Pygame game demonstrating basic game development concepts.

#### Risks and Considerations
- Potential issues with performance due to frequent redraws and updates.
- Need for thorough testing to ensure all edge cases are handled correctly.

#### Items to Confirm
- Verify that the game runs smoothly without crashes.
- Test collision detection and scoring functionality.
- Ensure proper resource management and cleanup.

### Code Diff to Review
```python
import pygame
import random
import sys

# Global variables
screen = None
playerX = 100
playerY = 100
vx = 0
vy = 0
enemyList = []
scoreValue = 0
runningGame = True

WIDTH = 640
HEIGHT = 480
PLAYER_SIZE = 30
ENEMY_SIZE = 25
SPEED = 5

# Initialize game
def initGame():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bad Smelly Pygame")
    for i in range(9):
        enemyList.append([random.randint(0, WIDTH-ENEMY_SIZE), random.randint(0, HEIGHT-ENEMY_SIZE)])

# Move player based on key inputs
def movePlayer(keys):
    global playerX, playerY, vx, vy
    if keys[pygame.K_LEFT]:
        vx = -SPEED
    elif keys[pygame.K_RIGHT]:
        vx = SPEED
    else:
        vx = 0
    if keys[pygame.K_UP]:
        vy = -SPEED
    elif keys[pygame.K_DOWN]:
        vy = SPEED
    else:
        vy = 0
    playerX += vx
    playerY += vy
    if playerX < 0: playerX = 0
    if playerX > WIDTH-PLAYER_SIZE: playerX = WIDTH-PLAYER_SIZE
    if playerY < 0: playerY = 0
    if playerY > HEIGHT-PLAYER_SIZE: playerY = HEIGHT-PLAYER_SIZE

# Draw everything on the screen
def drawEverything():
    global screen
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 0), (playerX, playerY, PLAYER_SIZE, PLAYER_SIZE))
    for e in enemyList:
        pygame.draw.rect(screen, (255, 0, 0), (e[0], e[1], ENEMY_SIZE, ENEMY_SIZE))
    font = pygame.font.SysFont(None, 36)
    text = font.render("Score: " + str(scoreValue), True, (255, 255, 255))
    screen.blit(text, (10, 10))
    pygame.display.flip()

# Check for collisions between player and enemies
def checkCollision():
    global scoreValue
    for e in enemyList:
        if (playerX < e[0] + ENEMY_SIZE and
            playerX + PLAYER_SIZE > e[0] and
            playerY < e[1] + ENEMY_SIZE and
            playerY + PLAYER_SIZE > e[1]):
            scoreValue += 1
            e[0] = random.randint(0, WIDTH-ENEMY_SIZE)
            e[1] = random.randint(0, HEIGHT-ENEMY_SIZE)

# Main game loop
def mainLoop():
    global runningGame
    clock = pygame.time.Clock()
    while runningGame:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runningGame = False
        keys = pygame.key.get_pressed()
        movePlayer(keys)
        checkCollision()
        drawEverything()
        clock.tick(27)

# End game and clean up resources
def endGame():
    pygame.quit()
    sys.exit()

# Entry point
if __name__ == "__main__":
    initGame()
    mainLoop()
    endGame()
```

This code snippet sets up a basic Pygame game with a player-controlled rectangle moving around the screen, avoiding red enemy rectangles. The player's score increases when they collide with an enemy. The game loop handles events, updates player position, checks for collisions, and draws everything to the screen.