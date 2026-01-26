# hipismo_runner.py
# Hipismo Runner – nome do jogador + placar final

import pygame
import sys
import random
import json
import os

pygame.init()
WIDTH, HEIGHT = 900, 600
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
    "p1": {"w": 36, "h": 48, "color": AZUL, "jump": 13, "grav": 0.72},
    "p2": {"w": 36, "h": 48, "color": (220, 20, 60), "jump": 13, "grav": 0.72}, # Vermelho
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
# --- SUBSTITUA A CLASSE PLAYER INTEIRA POR ISSO ---
class Player:
    def __init__(self, tipo, y_chao):
        p = PERSONAGENS[tipo]
        self.w, self.h = p["w"], p["h"]
        self.color = p["color"]
        self.jump_force = p["jump"]
        self.gravity = p["grav"]
        self.y_chao = y_chao # Cada jogador tem seu próprio chão
        
        # Posição inicial baseada no chão específico
        self.rect = pygame.Rect(110, self.y_chao - self.h, self.w, self.h)
        self.vy = 0
        self.on_ground = True
        self.vivo = True 

    def jump(self):
        if self.on_ground and self.vivo:
            self.vy = -self.jump_force
            self.on_ground = False

    def update(self):
        if not self.vivo:
            return # Se morreu, congela

        if not self.on_ground:
            self.vy += self.gravity
            self.rect.y += int(self.vy)
            
            # Colisão com o chão específico deste jogador
            if self.rect.bottom >= self.y_chao:
                self.rect.bottom = self.y_chao
                self.vy = 0
                self.on_ground = True

    def draw(self):
        # Desenha cor normal se vivo, cinza se morreu
        cor = self.color if self.vivo else (150, 150, 150)
        pygame.draw.rect(tela, cor, self.rect, border_radius=6)

# ---------------- OBSTÁCULOS ----------------
OBSTACLE_W = 56
OBSTACLE_H = 36

class Obstacle:
    def __init__(self, x, speed, y_chao):
        self.y_chao = y_chao
        self.rect = pygame.Rect(x, self.y_chao - OBSTACLE_H, OBSTACLE_W, OBSTACLE_H)
        self.speed = speed

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)

    def draw(self):
        # Desenho adaptado para usar self.y_chao
        post_w = 6
        post_h = OBSTACLE_H + 16

        left_post = pygame.Rect(self.rect.left, self.y_chao - post_h, post_w, post_h)
        right_post = pygame.Rect(self.rect.right - post_w, self.y_chao - post_h, post_w, post_h)

        pygame.draw.rect(tela, MARROM, left_post)
        pygame.draw.rect(tela, MARROM, right_post)

        bar_count = 3
        gap = OBSTACLE_H // (bar_count + 1)

        for i in range(bar_count):
            y = (self.y_chao - post_h) + gap * (i + 1)
            bar = pygame.Rect(left_post.right, y, OBSTACLE_W - post_w * 2, 6)
            pygame.draw.rect(tela, AMARELO, bar, border_radius=3)
            pygame.draw.line(tela, BRANCO, bar.topleft, bar.topright, 1)

# --- SUBSTITUA A CLASSE OBSTACLEMANAGER INTEIRA ---
class ObstacleManager:
    def __init__(self, y_chao):
        self.obstacles = []
        self.timer = 0
        self.speed = 6.0
        self.y_chao = y_chao # Saber onde criar o obstaculo

    def update(self, dt_ms, score):
        self.speed = 6.0 + min(4.0, max(0, (score - 1500) / 1200.0))

        self.timer += dt_ms
        if self.timer > random.randint(1200, 2200):
            self.timer = 0
            gap = random.randint(260, 560)
            x = WIDTH + gap
            if self.obstacles:
                x = max(x, self.obstacles[-1].rect.right + gap)
            # Passa o y_chao para o obstáculo novo
            self.obstacles.append(Obstacle(x, self.speed, self.y_chao))

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
def tela_regras():
    fonte_titulo = pygame.font.SysFont("Arial", 40, bold=True)
    fonte_texto = pygame.font.SysFont("Arial", 24)
    
    # Botão de Voltar
    btn_voltar = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)

    while True:
        tela.fill(CINZA)
        
        # Título
        titulo = fonte_titulo.render("REGRAS DO JOGO", True, PRETO)
        tela.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 50))

        # Texto das regras (Lista de strings)
        linhas = [
            "O objetivo é sobreviver o maior tempo possível.",
            "Quem bater no obstáculo primeiro perde.",
            "Se ambos baterem, ganha quem durou mais tempo.",
            "",
            "CONTROLES:",
            "Jogador 1 (Tela de Cima): Tecla W",
            "Jogador 2 (Tela de Baixo): Seta para CIMA",
            "",
            "Pressione ESC a qualquer momento para sair."
        ]

        # Desenhar cada linha centralizada
        y = 120
        for linha in linhas:
            texto = fonte_texto.render(linha, True, PRETO)
            tela.blit(texto, (WIDTH//2 - texto.get_width()//2, y))
            y += 35

        # Desenhar Botão Voltar
        pygame.draw.rect(tela, AMARELO, btn_voltar, border_radius=10)
        pygame.draw.rect(tela, PRETO, btn_voltar, 2, border_radius=10)
        
        txt_btn = fonte_texto.render("VOLTAR", True, PRETO)
        tela.blit(txt_btn, (btn_voltar.centerx - txt_btn.get_width()//2, btn_voltar.centery - txt_btn.get_height()//2))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1: # Clique esquerdo
                    if btn_voltar.collidepoint(e.pos):
                        return # Sai da função regras e volta pro menu

def tela_menu():
    fonte = pygame.font.SysFont("Arial", 40, bold=True)
    
    # Definição dos Retângulos dos Botões (x, y, largura, altura)
    btn_jogar = pygame.Rect(WIDTH//2 - 100, 200, 200, 60)
    btn_regras = pygame.Rect(WIDTH//2 - 100, 300, 200, 60)

    while True:
        tela.fill(VERDE) # Fundo verde estilo grama

        # Título do Jogo
        titulo = fonte.render("HIPISMO RUNNER", True, BRANCO)
        tela.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 80))

        # --- Desenhar Botão JOGAR ---
        # Detecta se o mouse está em cima para mudar a cor (efeito hover)
        mouse_pos = pygame.mouse.get_pos()
        cor_jogar = AMARELO if btn_jogar.collidepoint(mouse_pos) else (200, 150, 0)
        
        pygame.draw.rect(tela, cor_jogar, btn_jogar, border_radius=15)
        pygame.draw.rect(tela, BRANCO, btn_jogar, 3, border_radius=15) # Borda
        
        txt_jogar = fonte.render("JOGAR", True, PRETO)
        tela.blit(txt_jogar, (btn_jogar.centerx - txt_jogar.get_width()//2, btn_jogar.centery - txt_jogar.get_height()//2))

        # --- Desenhar Botão REGRAS ---
        cor_regras = AMARELO if btn_regras.collidepoint(mouse_pos) else (200, 150, 0)
        
        pygame.draw.rect(tela, cor_regras, btn_regras, border_radius=15)
        pygame.draw.rect(tela, BRANCO, btn_regras, 3, border_radius=15) # Borda
        
        txt_regras = fonte.render("REGRAS", True, PRETO)
        tela.blit(txt_regras, (btn_regras.centerx - txt_regras.get_width()//2, btn_regras.centery - txt_regras.get_height()//2))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1: # Botão esquerdo do mouse
                    if btn_jogar.collidepoint(e.pos):
                        return # Sai do menu e vai pro jogo
                    
                    if btn_regras.collidepoint(e.pos):
                        tela_regras() # Entra na tela de regras (e espera voltar)

def tela_nomes_dupla():
    nomes = ["", ""] # Lista para guardar [Nome1, Nome2]
    atual = 0 # 0 = editando P1, 1 = editando P2
    fonte = pygame.font.SysFont("Arial", 36)

    while True:
        tela.fill(VERDE)

        # Muda o título dependendo de quem estamos digitando
        if atual == 0:
            msg = "Nome do Jogador 1 (Azul):"
        else:
            msg = "Nome do Jogador 2 (Vermelho):"
            
        titulo = fonte.render(msg, True, BRANCO)
        nome_txt = fonte.render(nomes[atual] + "|", True, BRANCO)

        # Desenha centralizado
        tela.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 120))
        tela.blit(nome_txt, (WIDTH//2 - nome_txt.get_width()//2, 180))
        
        # Instrução pequena
        info = pygame.font.SysFont("Arial", 20).render("Enter para confirmar", True, BRANCO)
        tela.blit(info, (WIDTH//2 - info.get_width()//2, 250))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    # Só avança se tiver digitado algo
                    if nomes[atual].strip():
                        if atual == 0:
                            atual = 1 # Vai para o Jogador 2
                        else:
                            return nomes[0], nomes[1] # Retorna os dois nomes
                
                elif e.key == pygame.K_BACKSPACE:
                    nomes[atual] = nomes[atual][:-1]
                
                # Limite de 12 caracteres
                elif len(nomes[atual]) < 12 and e.unicode.isprintable():
                    nomes[atual] += e.unicode
        
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
def jogo_multiplayer(nome1, nome2): 
    # Setup inicial
    chao_p1 = HEIGHT // 2 - 20
    chao_p2 = HEIGHT - 20
    player1 = Player("p1", chao_p1)
    player2 = Player("p2", chao_p2)
    manager1 = ObstacleManager(chao_p1)
    manager2 = ObstacleManager(chao_p2)
    score1 = 0
    score2 = 0
    last = pygame.time.get_ticks()

    # Loop Principal do Jogo
    while player1.vivo or player2.vivo:
        # 1. Cálculo do tempo (Delta Time)
        now = pygame.time.get_ticks()
        dt = now - last
        last = now

        # 2. Eventos (Teclado e Fechar Jogo)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                # Controles Jogador 1 (W)
                if e.key == pygame.K_w and player1.vivo:
                    player1.jump()
                # Controles Jogador 2 (Seta Cima)
                if e.key == pygame.K_UP and player2.vivo:
                    player2.jump()
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # 3. Lógica e Atualização (Física)
        
        # --- Atualização Jogador 1 ---
        if player1.vivo:
            player1.update()
            manager1.update(dt, score1)
            if manager1.collide(player1.rect):
                player1.vivo = False # Morreu
            else:
                score1 += dt // 5
        
        # --- Atualização Jogador 2 ---
        if player2.vivo:
            player2.update()
            manager2.update(dt, score2)
            if manager2.collide(player2.rect):
                player2.vivo = False # Morreu
            else:
                score2 += dt // 5

        # 4. Desenho na Tela
        tela.fill((135, 206, 235)) 
        
        # Cenário
        pygame.draw.line(tela, PRETO, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 4)
        pygame.draw.rect(tela, VERDE, (0, chao_p1, WIDTH, 20))
        pygame.draw.rect(tela, VERDE, (0, chao_p2, WIDTH, 20))

        # Desenhar Personagens e Obstáculos
        player1.draw(); manager1.draw()
        player2.draw(); manager2.draw()

        # HUD (Placar e Nomes)
        fonte = pygame.font.SysFont("Arial", 20, bold=True)
        
        # Nome 1 no topo
        tela.blit(fonte.render(f"{nome1}: {score1}", True, AZUL), (10, 10))
        
        # Nome 2 na metade
        tela.blit(fonte.render(f"{nome2}: {score2}", True, (220, 0, 0)), (10, HEIGHT//2 + 10))

        # Mensagens de "Bateu"
        if not player1.vivo:
            msg = fonte.render(f"{nome1} BATEU!", True, PRETO)
            tela.blit(msg, (WIDTH//2 - 50, chao_p1 - 100))
        
        if not player2.vivo:
            msg = fonte.render(f"{nome2} BATEU!", True, PRETO)
            tela.blit(msg, (WIDTH//2 - 50, chao_p2 - 100))

        pygame.display.update()
        CLOCK.tick(FPS)

    # Retorno final com os nomes corretos
    if score1 > score2:
        return nome1, score1, score2
    elif score2 > score1:
        return nome2, score1, score2
    else:
        return "EMPATE", score1, score2

def tela_vencedor(vencedor, score1, score2):
    fonte_grande = pygame.font.SysFont("Arial", 60, bold=True)
    fonte_media = pygame.font.SysFont("Arial", 30)

    while True:
        tela.fill(CINZA)
        
        # Mostra quem ganhou
        texto_venc = f"VENCEDOR: {vencedor}"
        if vencedor == "EMPATE":
            cor = PRETO
        elif vencedor == "JOGADOR 1":
            cor = AZUL
        else:
            cor = (220, 20, 60) # Vermelho

        surf_venc = fonte_grande.render(texto_venc, True, cor)
        tela.blit(surf_venc, (WIDTH//2 - surf_venc.get_width()//2, 150))

        # Mostra os pontos finais
        txt_s1 = fonte_media.render(f"P1 (Azul): {score1}", True, AZUL)
        txt_s2 = fonte_media.render(f"P2 (Vermelho): {score2}", True, (220, 20, 60))
        
        tela.blit(txt_s1, (WIDTH//2 - txt_s1.get_width()//2, 250))
        tela.blit(txt_s2, (WIDTH//2 - txt_s2.get_width()//2, 290))

        cmd = fonte_media.render("Pressione R para Reiniciar ou ESC para Sair", True, PRETO)
        tela.blit(cmd, (WIDTH//2 - cmd.get_width()//2, 450))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return # Volta para o main e reinicia
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

# ---------------- MAIN ----------------
def main():
    while True:
        # 1. Tela de Nomes
        n1, n2 = tela_nomes_dupla()
        
        # 2. Tela de Menu (NOVO)
        # O código fica preso aqui até a pessoa clicar em "JOGAR"
        tela_menu()
        
        # 3. O Jogo começa
        vencedor_nome, s1, s2 = jogo_multiplayer(n1, n2)
        
        # 4. Tela de Vencedor
        tela_vencedor(vencedor_nome, s1, s2)

if __name__ == "__main__":
    main()

