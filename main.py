# hipismo_runner.py
# Hipismo Runner – nome do jogador + placar final

import pygame
import sys
import random
import json
import os

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

#Pontuação
HIGHSCORES_FILE = "highscores.json"
MAX_HIGHSCORES = 10

GROUND_Y = HEIGHT - 70

# ---------------- PERSONAGENS ----------------
PERSONAGENS = {
    "corredor": {"w": 36, "h": 48, "color": AZUL, "jump": 13, "grav": 0.72},
    "cavalo":   {"w": 64, "h": 48, "color": MARROM, "jump": 15, "grav": 0.95},
}

#Placar

def load_highscores():
    """Retorna lista [{'name':..., 'score':...}, ...] ordenada (maior primeiro)."""
    if not os.path.exists(HIGHSCORES_FILE):
        return []
    try:
        with open(HIGHSCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                cleaned = []
                for item in data:
                    if isinstance(item, dict) and "name" in item and "score" in item:
                        cleaned.append({"name": str(item["name"]), "score": int(item["score"])})
                cleaned.sort(key=lambda x: x["score"], reverse=True)
                return cleaned[:MAX_HIGHSCORES]
    except Exception:
        pass
    return []

def save_highscores(highscores):
    """Salva lista de highscores (já ordenada/truncada)."""
    try:
        highscores = sorted(highscores, key=lambda x: x["score"], reverse=True)[:MAX_HIGHSCORES]
        with open(HIGHSCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(highscores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Erro ao salvar highscores:", e)

def update_highscores(name, score):
    """Adiciona (name,score) e retorna a lista atualizada do Top10."""
    name = name.strip() if isinstance(name, str) else "Anon"
    if not name:
        name = "Anon"
    highscores = load_highscores()
    highscores.append({"name": name, "score": int(score)})
    highscores.sort(key=lambda x: x["score"], reverse=True)
    highscores = highscores[:MAX_HIGHSCORES]
    save_highscores(highscores)
    return highscores

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

# ---------------- TELAS ----------------
def tela_nome():
    nome = ""
    fonte = pygame.font.SysFont("Arial", 36)
    while True:
        tela.fill(VERDE)
        titulo = fonte.render("Digite seu nome:", True, BRANCO)
        nome_txt = fonte.render(nome + "|", True, BRANCO)

        tela.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 120))
        tela.blit(nome_txt, (WIDTH//2 - nome_txt.get_width()//2, 180))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and nome.strip():
                    return nome
                elif e.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                elif len(nome) < 12 and e.unicode.isprintable():
                    nome += e.unicode

        pygame.display.update()
        CLOCK.tick(30)

def tela_placar(nome, score):
    fonte_titulo = pygame.font.SysFont("Arial", 48, bold=True)
    fonte = pygame.font.SysFont("Arial", 28)
    small = pygame.font.SysFont("Arial", 18)

    # atualiza highscores e obtém a lista atualizada
    highscores = update_highscores(nome, score)

    # (opcional) debug no console — comente se não quiser ver isso
    print("[HS] highscores atualizados:", highscores)

    while True:
        tela.fill(CINZA)

        tela.blit(fonte_titulo.render("PLACAR FINAL", True, PRETO), (WIDTH//2 - 160, 24))
        tela.blit(fonte.render(f"Jogador: {nome}", True, PRETO), (WIDTH//2 - 160, 90))
        tela.blit(fonte.render(f"Pontuação: {score}", True, PRETO), (WIDTH//2 - 160, 130))

        # mostra Top10 com colocação
        tela.blit(fonte.render("Top 10:", True, PRETO), (WIDTH//2 + 80, 80))
        start_y = 120
        for i, entry in enumerate(highscores, start=1):
            rank_text = f"{i}. {entry['name']} — {entry['score']}"
            tela.blit(small.render(rank_text, True, PRETO), (WIDTH//2 + 80, start_y + i*22))

        tela.blit(fonte.render("Pressione R para jogar novamente", True, PRETO), (WIDTH//2 - 200, HEIGHT - 90))
        tela.blit(fonte.render("ESC para sair", True, PRETO), (WIDTH//2 + 80, HEIGHT - 90))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        pygame.display.update()
        CLOCK.tick(30)


# ---------------- JOGO ----------------
def jogo(nome):
    player = Player()
    obstacles = ObstacleManager()
    score = 0
    last = pygame.time.get_ticks()
    game_over = False

    while not game_over:
        now = pygame.time.get_ticks()
        dt = now - last
        last = now

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_SPACE, pygame.K_UP):
                    player.jump()

        player.update()
        obstacles.update(dt, score)
        if obstacles.collide(player.rect):
            game_over = True

        score += dt // 5

        tela.fill((135, 206, 235))
        pygame.draw.rect(tela, VERDE, (0, GROUND_Y, WIDTH, HEIGHT))
        player.draw()
        obstacles.draw()

        fonte = pygame.font.SysFont("Arial", 20)
        tela.blit(fonte.render(f"{nome} | Score: {score}", True, PRETO), (10, 10))

        pygame.display.update()
        CLOCK.tick(FPS)

    return score

# ---------------- MAIN ----------------
def main():
    if not os.path.exists(HIGHSCORES_FILE):
        save_highscores([])

    while True:
        nome = tela_nome()
        score = jogo(nome)
        tela_placar(nome, score)

if __name__ == "__main__":
    main()
