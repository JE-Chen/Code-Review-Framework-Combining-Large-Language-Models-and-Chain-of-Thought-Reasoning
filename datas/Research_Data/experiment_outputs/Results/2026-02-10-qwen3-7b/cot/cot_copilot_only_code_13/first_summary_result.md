### 🧪 PR Summary Template

---

### ✅ Key Changes
- Added game loop and event handling
- Implemented player movement and collision detection
- Added score tracking and enemy spawning

---

### 📌 Impact Scope
- Affected: `initGame`, `mainLoop`, `checkCollision`, `drawEverything`
- Functional Changes: Game mechanics, rendering, and scoring

---

### 💡 Purpose of Changes
- Improve game mechanics and user experience
- Ensure game runs with consistent rules and visual feedback

---

### 🔍 Risks and Considerations
- Enemy positions are updated in-place; may need refactoring
- No error handling for invalid inputs
- Missing docstrings and tests

---

### 📝 Items to Confirm
1. Collision detection logic is correct
2. Enemy spawning is random and within bounds
3. Score is updated and displayed
4. Game loop handles quitting and rendering

---

### 📝 Code Diff Summary
```python
import pygame
import random
import sys

screen = None
playerX = 200
playerY = 200
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

def initGame():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bad Smelly Game")
    for i in range(7):
        enemyList.append([random.randint(0, WIDTH-ENEMY_SIZE), random.randint(0, HEIGHT-ENEMY_SIZE)])

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
        clock.tick(30)

def endGame():
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    initGame()
    mainLoop()
    endGame()
```

---

### 📌 Final Notes
- **Code Quality**: Clean and readable, with clear separation of concerns.
- **Completeness**: Missing docstrings and tests, but core functionality is solid.
- **Team Consistency**: Follows standard Python and Pygame conventions.