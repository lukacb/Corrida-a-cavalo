# hipismo_runner.py
# Hipismo Runner – nome do jogador + placar final

import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 900, 400
tela = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hipismo Runner")

CLOCK = pygame.time.Clock()
FPS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
AMARELO = (255, 200, 0)
MARROM = (120, 72, 18)
AZUL = (20, 120, 220)
CINZA = (200, 200, 200)

GROUND_Y = HEIGHT - 70

# ---------------- PERSONAGENS ----------------
PERSONAGENS = {
    "corredor": {"w": 36, "h": 48, "color": AZUL, "jump": 13, "grav": 0.72},
    "cavalo":   {"w": 64, "h": 48, "color": MARROM, "jump": 15, "grav": 0.95},
}

# ---------------- JOGADOR ----------------
class Player:
    def __init__(self, tipo="corredor"):
        p = PERSONAGENS[tipo]
        self.w, self.h = p["w"], p["h"]
        self.color = p["color"]
        self.jump_force = p["jump"]
        self.gravity = p["grav"]
        self.rect = pygame.Rect(110, GROUND_Y - self.h, self.w, self.h)
        self.vy = 0
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vy = -self.jump_force
            self.on_ground = False

    def update(self):
        if not self.on_ground:
            self.vy += self.gravity
            self.rect.y += int(self.vy)
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.vy = 0
                self.on_ground = True

    def draw(self):
        pygame.draw.rect(tela, self.color, self.rect, border_radius=6)

# ---------------- OBSTÁCULOS ----------------
OBSTACLE_W = 56
OBSTACLE_H = 36

class Obstacle:
    def __init__(self, x, speed):
        self.rect = pygame.Rect(x, GROUND_Y - OBSTACLE_H, OBSTACLE_W, OBSTACLE_H)
        self.speed = speed

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)

    def draw(self):
        post_w = 6
        post_h = OBSTACLE_H + 16

        left_post = pygame.Rect(self.rect.left, GROUND_Y - post_h, post_w, post_h)
        right_post = pygame.Rect(self.rect.right - post_w, GROUND_Y - post_h, post_w, post_h)

        pygame.draw.rect(tela, MARROM, left_post)
        pygame.draw.rect(tela, MARROM, right_post)

        bar_count = 3
        gap = OBSTACLE_H // (bar_count + 1)

        for i in range(bar_count):
            y = (GROUND_Y - post_h) + gap * (i + 1)
            bar = pygame.Rect(left_post.right, y, OBSTACLE_W - post_w * 2, 6)
            pygame.draw.rect(tela, AMARELO, bar, border_radius=3)
            pygame.draw.line(tela, BRANCO, bar.topleft, bar.topright, 1)

# ---------------- GERENCIADOR ----------------
class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.timer = 0
        self.speed = 6.0

    def update(self, dt_ms, score):
        # aceleração gradual
        self.speed = 6.0 + min(4.0, max(0, (score - 1500) / 1200.0))

        self.timer += dt_ms
        if self.timer > random.randint(1200, 2200):
            self.timer = 0
            gap = random.randint(260, 560)
            x = WIDTH + gap
            if self.obstacles:
                x = max(x, self.obstacles[-1].rect.right + gap)
            self.obstacles.append(Obstacle(x, self.speed))

        for obs in self.obstacles[:]:
            obs.update(dt_ms / 16.6)
            if obs.rect.right < 0:
                self.obstacles.remove(obs)

    def draw(self):
        for o in self.obstacles:
            o.draw()

    def collide(self, rect):
        return any(o.rect.colliderect(rect) for o in self.obstacles)


