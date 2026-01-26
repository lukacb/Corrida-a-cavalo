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
    small = pygame.font.SysFont("Arial", 20)
    tiny = pygame.font.SysFont("Arial", 16)

    # atualiza highscores e obtém a lista atualizada
    highscores = update_highscores(nome, score)

    # layout coordinates
    padding = 24
    left_x = padding
    right_x = WIDTH // 2 + padding
    title_y = 24
    info_y = 100
    top10_start_y = info_y
    bottom_y = HEIGHT - 70

    while True:
        tela.fill(CINZA)

        # Título (centrado)
        titulo_surf = fonte_titulo.render("PLACAR FINAL", True, PRETO)
        tela.blit(titulo_surf, ((WIDTH - titulo_surf.get_width()) // 2, title_y))

        # Caixa esquerda: jogador e sua pontuação
        jogador_title = fonte.render("Resultado", True, PRETO)
        tela.blit(jogador_title, (left_x, info_y))
        tela.blit(small.render(f"Jogador: {nome}", True, PRETO), (left_x, info_y + 40))
        tela.blit(small.render(f"Pontuação: {score}", True, PRETO), (left_x, info_y + 72))

        # Caixa direita: Top 10
        top10_title = fonte.render("Top 10", True, PRETO)
        tela.blit(top10_title, (right_x, top10_start_y))
        # desenha um fundo leve atrás da lista para contraste (opcional)
        list_bg_rect = pygame.Rect(right_x - 8, top10_start_y + 36, WIDTH - right_x - padding, min(260, 30 + len(highscores)*26))
        pygame.draw.rect(tela, (240,240,240), list_bg_rect)
        pygame.draw.rect(tela, (200,200,200), list_bg_rect, 1)

        # Renderiza cada entrada do Top10 em linhas separadas (sem sobreposição)
        line_y = top10_start_y + 44
        for i, entry in enumerate(highscores, start=1):
            rank_text = f"{i}. {entry['name']}"
            score_text = f"{entry['score']}"
            rank_surf = small.render(rank_text, True, PRETO)
            score_surf = small.render(score_text, True, PRETO)
            tela.blit(rank_surf, (right_x, line_y))
            # alinha a pontuação à direita da área do Top10
            tela.blit(score_surf, (right_x + list_bg_rect.width - score_surf.get_width() - 8, line_y))
            line_y += 26  # espaçamento vertical consistente

        # Comandos na parte inferior (centralizados, sem sobreposição)
        cmd1 = tiny.render("Pressione R para jogar novamente", True, PRETO)
        cmd2 = tiny.render("ESC para sair", True, PRETO)
        # posiciona os dois com espaço entre eles
        total_cmd_width = cmd1.get_width() + 24 + cmd2.get_width()
        start_cmd_x = (WIDTH - total_cmd_width) // 2
        tela.blit(cmd1, (start_cmd_x, bottom_y))
        tela.blit(cmd2, (start_cmd_x + cmd1.get_width() + 24, bottom_y))

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
