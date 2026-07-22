import pygame
import random
import math
import time
import sys

pygame.init()

W = 800
H = 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Totally Fine Game")

CLOCK_THING = pygame.time.Clock()

PLAYER = {"x": 400, "y": 300, "hp": 100, "score": 0}
ENEMIES = []
BULLETS = []
STRANGE_FLAGS = {"panic": False}
MAGIC = 17

FONT = pygame.font.SysFont(None, 24)


def do_the_whole_game_because_why_not():
    running = True
    spawn_timer = 0
    frame_counter = 0
    last_score_check = -1

    while running:
        frame_counter += 1
        spawn_timer += 1
        CLOCK_THING.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            PLAYER["x"] -= 4
        if keys[pygame.K_d]:
            PLAYER["x"] += 4
        if keys[pygame.K_w]:
            PLAYER["y"] -= 4
        if keys[pygame.K_s]:
            PLAYER["y"] += 4

        if PLAYER["x"] < 0:
            PLAYER["x"] = 0
        if PLAYER["x"] > W:
            PLAYER["x"] = W
        if PLAYER["y"] < 0:
            PLAYER["y"] = 0
        if PLAYER["y"] > H:
            PLAYER["y"] = H

        if keys[pygame.K_SPACE]:
            if frame_counter % 10 == 0:
                BULLETS.append({
                    "x": PLAYER["x"],
                    "y": PLAYER["y"],
                    "vx": random.choice([-7, 7]),
                    "vy": random.choice([-7, 7])
                })

        if spawn_timer > MAGIC:
            spawn_timer = 0
            ENEMIES.append({
                "x": random.randint(0, W),
                "y": random.randint(0, H),
                "speed": random.random() * 2 + 1,
                "life": random.randint(1, 3)
            })

        for e in ENEMIES:
            dx = PLAYER["x"] - e["x"]
            dy = PLAYER["y"] - e["y"]
            dist = math.sqrt(dx * dx + dy * dy) + 0.0001
            e["x"] += dx / dist * e["speed"]
            e["y"] += dy / dist * e["speed"]

        for b in BULLETS:
            b["x"] += b["vx"]
            b["y"] += b["vy"]

        try:
            for e in ENEMIES[:]:
                for b in BULLETS[:]:
                    if abs(e["x"] - b["x"]) < 10 and abs(e["y"] - b["y"]) < 10:
                        e["life"] -= 1
                        BULLETS.remove(b)
                        if e["life"] <= 0:
                            PLAYER["score"] += 1
                            ENEMIES.remove(e)
        except:
            pass

        for e in ENEMIES[:]:
            if abs(e["x"] - PLAYER["x"]) < 15 and abs(e["y"] - PLAYER["y"]) < 15:
                PLAYER["hp"] -= 1
                STRANGE_FLAGS["panic"] = True
                if PLAYER["hp"] <= 0:
                    running = False

        if PLAYER["score"] != last_score_check:
            last_score_check = PLAYER["score"]
            if PLAYER["score"] % 5 == 0:
                PLAYER["hp"] += 3

        screen.fill((20, 20, 20))

        pygame.draw.rect(screen, (0, 200, 0),
                         (PLAYER["x"], PLAYER["y"], 20, 20))

        for e in ENEMIES:
            pygame.draw.circle(screen, (200, 50, 50),
                               (int(e["x"]), int(e["y"])), 10)

        for b in BULLETS:
            pygame.draw.circle(screen, (200, 200, 50),
                               (int(b["x"]), int(b["y"])), 4)

        hud = FONT.render(
            f"HP:{PLAYER['hp']} Score:{PLAYER['score']} Panic:{STRANGE_FLAGS['panic']}",
            True, (255, 255, 255)
        )
        screen.blit(hud, (10, 10))

        if frame_counter % 300 == 0:
            STRANGE_FLAGS["panic"] = False

        pygame.display.flip()

    print("Game Over. Final score:", PLAYER["score"])
    time.sleep(1)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    do_the_whole_game_because_why_not()