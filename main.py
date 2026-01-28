# hipismo_runner.py
import pygame
import sys
import random
import json
import os

pygame.init()
pygame.mixer.init()


WIDTH, HEIGHT = 900, 600
tela = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hipismo Runner")

CLOCK = pygame.time.Clock()
FPS = 60

# ---------------- CENÁRIO (IMAGEM) ----------------
try:
    BG_IMAGE = pygame.image.load("hipodromo_bg.png").convert()
    BG_IMAGE = pygame.transform.scale(BG_IMAGE, (WIDTH, HEIGHT))
except Exception as e:
    BG_IMAGE = None
    print("Aviso: não foi possível carregar 'hipodromo_bg.png'. Erro:", e)

try:
    MENU_BG = pygame.image.load("menu_bg.png").convert()
    MENU_BG = pygame.transform.scale(MENU_BG, (WIDTH, HEIGHT))
except Exception as e:
    MENU_BG = None
    print("Aviso: Imagem 'menu_bg.png' não encontrada.")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
AMARELO = (255, 200, 0)
MARROM = (120, 72, 18)
AZUL = (20, 120, 220)
CINZA = (200, 200, 200)

OPCOES_CAVALOS = [
    {"nome": "Relâmpago (Azul)", "cor": AZUL},
    {"nome": "Fúria (Vermelho)", "cor": (220, 20, 60)},
    {"nome": "Fantasma (Cinza)", "cor": (100, 100, 100)},
    {"nome": "Sombra (Preto)", "cor": (20, 20, 20)},
    {"nome": "Ouro (Amarelo)", "cor": (218, 165, 32)},
    {"nome": "Esmeralda (Verde)", "cor": (0, 100, 0)},
    {"nome": "Violeta (Roxo)", "cor": (138, 43, 226)},
]
# ---------------- MÚSICA ----------------
try:
    pygame.mixer.music.load("cavalopreto.ogg")
    pygame.mixer.music.set_volume(0.4)  # volume de 0.0 a 1.0
except Exception as e:
    print("Erro ao carregar música:", e)

#Pontuação
HIGHSCORES_FILE = "highscores.json"
MAX_HIGHSCORES = 10

GROUND_Y = HEIGHT - 70

# ---------------- PERSONAGENS ----------------
PERSONAGENS = {
    "p1": {"w": 36, "h": 48, "color": AZUL, "jump": 13, "grav": 0.72},
    "p2": {"w": 36, "h": 48, "color": (220, 20, 60), "jump": 13, "grav": 0.72}, # Vermelho
}


#---------------------SELECAO CAVALO----------------
def tela_selecao_cavalos(nome1, nome2):
    fonte = pygame.font.SysFont("Arial", 30)
    fonte_nome = pygame.font.SysFont("Arial", 40, bold=True)
    
    idx1 = 0
    idx2 = 1
    
    confirmado1 = False
    confirmado2 = False

    while True:
        tela.fill(VERDE)
        
        # --- LADO P1 (Esquerda) ---
        cor_fundo1 = (200, 255, 200) if confirmado1 else (150, 200, 150)
        pygame.draw.rect(tela, cor_fundo1, (0, 0, WIDTH//2, HEIGHT))
        
        # Nome P1
        txt_n1 = fonte_nome.render(nome1, True, PRETO)
        tela.blit(txt_n1, (WIDTH//4 - txt_n1.get_width()//2, 50))
        
        # Cavalo Selecionado P1
        cavalo1 = OPCOES_CAVALOS[idx1]
        pygame.draw.rect(tela, cavalo1["cor"], (WIDTH//4 - 40, 150, 80, 80), border_radius=10)
        txt_c1 = fonte.render(cavalo1["nome"], True, PRETO)
        tela.blit(txt_c1, (WIDTH//4 - txt_c1.get_width()//2, 250))

        # Status P1
        status1 = "PRONTO!" if confirmado1 else "Escolha com W/S e ESPAÇO"
        txt_s1 = fonte.render(status1, True, PRETO)
        tela.blit(txt_s1, (WIDTH//4 - txt_s1.get_width()//2, 350))

        # --- LADO P2 (Direita) ---
        cor_fundo2 = (200, 255, 200) if confirmado2 else (150, 200, 150)
        pygame.draw.rect(tela, cor_fundo2, (WIDTH//2, 0, WIDTH//2, HEIGHT))
        pygame.draw.line(tela, PRETO, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 5)

        # Nome P2
        txt_n2 = fonte_nome.render(nome2, True, PRETO)
        tela.blit(txt_n2, (3*WIDTH//4 - txt_n2.get_width()//2, 50))
        
        # Cavalo Selecionado P2
        cavalo2 = OPCOES_CAVALOS[idx2]
        pygame.draw.rect(tela, cavalo2["cor"], (3*WIDTH//4 - 40, 150, 80, 80), border_radius=10)
        txt_c2 = fonte.render(cavalo2["nome"], True, PRETO)
        tela.blit(txt_c2, (3*WIDTH//4 - txt_c2.get_width()//2, 250))

        # Status P2
        status2 = "PRONTO!" if confirmado2 else "Escolha com SETAS e ENTER"
        txt_s2 = fonte.render(status2, True, PRETO)
        tela.blit(txt_s2, (3*WIDTH//4 - txt_s2.get_width()//2, 350))

        pygame.display.update()


        if confirmado1 and confirmado2:
            pygame.time.delay(300) 
            return cavalo1["cor"], cavalo2["cor"]

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if e.type == pygame.KEYDOWN:
                # Controles P1
                if not confirmado1:
                    if e.key == pygame.K_w:
                        idx1 = (idx1 - 1) % len(OPCOES_CAVALOS)
                    elif e.key == pygame.K_s:
                        idx1 = (idx1 + 1) % len(OPCOES_CAVALOS)
                    elif e.key == pygame.K_SPACE:
                        confirmado1 = True
                elif e.key == pygame.K_SPACE: 
                    confirmado1 = False

                # Controles P2
                if not confirmado2:
                    if e.key == pygame.K_UP:
                        idx2 = (idx2 - 1) % len(OPCOES_CAVALOS)
                    elif e.key == pygame.K_DOWN:
                        idx2 = (idx2 + 1) % len(OPCOES_CAVALOS)
                    elif e.key == pygame.K_RETURN:
                        confirmado2 = True
                elif e.key == pygame.K_RETURN:
                    confirmado2 = False

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
    def __init__(self, tipo, y_chao, cor_personalizada=None):
        p = PERSONAGENS[tipo]
        self.w, self.h = p["w"], p["h"]
        
        if cor_personalizada:
            self.color = cor_personalizada
        else:
            self.color = p["color"]
        # ---------------------------

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
        # Desenha com a cor escolhida se estiver vivo, ou cinza se morreu
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
        post_w = 6
        post_h = OBSTACLE_H + 16

        left_post = pygame.Rect(self.rect.left, self.y_chao - post_h, post_w, post_h)
        right_post = pygame.Rect(self.rect.right - post_w, self.y_chao - post_h, post_w, post_h)

        pygame.draw.rect(tela, BRANCO, left_post)
        pygame.draw.rect(tela, BRANCO, right_post)

        bar_count = 3
        gap = OBSTACLE_H // (bar_count + 1)

        for i in range(bar_count):
            y = (self.y_chao - post_h) + gap * (i + 1)
            bar = pygame.Rect(left_post.right, y, OBSTACLE_W - post_w * 2, 6)
            
            pygame.draw.rect(tela, AZUL, bar, border_radius=3)
            
            pygame.draw.line(tela, BRANCO, bar.topleft, bar.topright, 1)

class ObstacleManager:
    def __init__(self, y_chao):
        self.obstacles = []
        self.timer = 0
        self.y_chao = y_chao

        # Configurações de velocidade
        self.BASE_SPEED = 8.0
        self.SPEED_STEP = 1.0      # quanto aumenta a cada 5000 pontos
        self.MAX_SPEED = 12.0      # limite máximo
        self.speed = self.BASE_SPEED

    def update(self, dt_ms, score):
        # --- AUMENTA A VELOCIDADE A CADA 2000 PONTOS ---
        nivel = score // 2000
        self.speed = self.BASE_SPEED + nivel * self.SPEED_STEP
        if self.speed > self.MAX_SPEED:
            self.speed = self.MAX_SPEED

        # Timer para gerar obstáculos
        self.timer += dt_ms
        if self.timer > random.randint(1200, 2200):
            self.timer = 0
            gap = random.randint(260, 560)
            x = WIDTH + gap
            if self.obstacles:
                x = max(x, self.obstacles[-1].rect.right + gap)

            self.obstacles.append(Obstacle(x, self.speed, self.y_chao))

        # Atualiza obstáculos existentes (normaliza dt para frames)
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
    
    # --- POSIÇÕES DOS BOTÕES (Ajustadas para baixo) ---
    # Antes eram 200, 300, 400. Agora baixamos todos em 100 pixels.
    btn_jogar = pygame.Rect(WIDTH//2 - 100, 300, 200, 60)
    btn_regras = pygame.Rect(WIDTH//2 - 100, 400, 200, 60)
    btn_sair = pygame.Rect(WIDTH//2 - 100, 500, 200, 60)

    while True:
        # --- DESENHO DO FUNDO ---
        if MENU_BG:
            tela.blit(MENU_BG, (0, 0))
        else:
            tela.fill(VERDE) 

        # (REMOVI A PARTE QUE DESENHAVA O TÍTULO TEXTO AQUI)
        # Como o MENU_BG já tem o título desenhado, não precisamos escrever por cima.

        mouse_pos = pygame.mouse.get_pos()

        # --- Botão JOGAR ---
        cor_jogar = AMARELO if btn_jogar.collidepoint(mouse_pos) else (200, 150, 0)
        pygame.draw.rect(tela, cor_jogar, btn_jogar, border_radius=15)
        pygame.draw.rect(tela, BRANCO, btn_jogar, 3, border_radius=15)
        txt_jogar = fonte.render("JOGAR", True, PRETO)
        tela.blit(txt_jogar, (btn_jogar.centerx - txt_jogar.get_width()//2, btn_jogar.centery - txt_jogar.get_height()//2))

        # --- Botão REGRAS ---
        cor_regras = AMARELO if btn_regras.collidepoint(mouse_pos) else (200, 150, 0)
        pygame.draw.rect(tela, cor_regras, btn_regras, border_radius=15)
        pygame.draw.rect(tela, BRANCO, btn_regras, 3, border_radius=15)
        txt_regras = fonte.render("REGRAS", True, PRETO)
        tela.blit(txt_regras, (btn_regras.centerx - txt_regras.get_width()//2, btn_regras.centery - txt_regras.get_height()//2))

        # --- Botão SAIR ---
        cor_sair = (255, 100, 100) if btn_sair.collidepoint(mouse_pos) else (200, 50, 50)
        pygame.draw.rect(tela, cor_sair, btn_sair, border_radius=15)
        pygame.draw.rect(tela, BRANCO, btn_sair, 3, border_radius=15)
        txt_sair = fonte.render("SAIR", True, PRETO)
        tela.blit(txt_sair, (btn_sair.centerx - txt_sair.get_width()//2, btn_sair.centery - txt_sair.get_height()//2))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1: 
                    if btn_jogar.collidepoint(e.pos): return 
                    if btn_regras.collidepoint(e.pos): tela_regras()
                    if btn_sair.collidepoint(e.pos): pygame.quit(); sys.exit()

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

def jogo_multiplayer(nome1, nome2, cor1, cor2):
    pygame.mixer.music.play(-1)  # -1 = loop infinito


    # Valores ajustados para se alinharem com a imagem do hipódromo
    chao_p1 = 355
    chao_p2 = 545
    
    # Passamos a cor escolhida (cor1/cor2) para cada Player
    player1 = Player("p1", chao_p1, cor_personalizada=cor1)
    player2 = Player("p2", chao_p2, cor_personalizada=cor2)
    
    # Gerenciadores de obstáculos
    manager1 = ObstacleManager(chao_p1)
    manager2 = ObstacleManager(chao_p2)
    
    score1 = 0
    score2 = 0
    last = pygame.time.get_ticks()

    # Loop Principal: Roda enquanto pelo menos um estiver vivo
    while player1.vivo or player2.vivo:
        # 1. Cálculo do tempo (Delta Time)
        now = pygame.time.get_ticks()
        dt = now - last
        last = now

        # 2. Eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                # Controles P1 (W)
                if e.key == pygame.K_w and player1.vivo:
                    player1.jump()
                # Controles P2 (Seta Cima)
                if e.key == pygame.K_UP and player2.vivo:
                    player2.jump()
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # 3. Lógica e Física
        
        # --- Atualização P1 ---
        if player1.vivo:
            player1.update()
            manager1.update(dt, score1)
            if manager1.collide(player1.rect):
                player1.vivo = False
            else:
                score1 += dt // 5
        
        # --- Atualização P2 ---
        if player2.vivo:
            player2.update()
            manager2.update(dt, score2)
            if manager2.collide(player2.rect):
                player2.vivo = False
            else:
                score2 += dt // 5

        # 4. Desenho
        # Se a imagem de fundo foi carregada, usa-a. Caso contrário, desenha o fundo padrão.
        if BG_IMAGE:
            tela.blit(BG_IMAGE, (0, 0))
        else:
            tela.fill((135, 206, 235)) # Céu
            # Cenário alternativo
            pygame.draw.line(tela, PRETO, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 4)
            pygame.draw.rect(tela, VERDE, (0, chao_p1, WIDTH, 20))
            pygame.draw.rect(tela, VERDE, (0, chao_p2, WIDTH, 20))

        # Desenha os jogadores  e obstáculos
        player1.draw(); manager1.draw()
        player2.draw(); manager2.draw()

        # HUD 
        fonte = pygame.font.SysFont("Arial", 20, bold=True)

        # === COORDENADAS DO PLACAR PRETO ===
        PLACAR_X = 40
        PLACAR_LARGURA = 220

        # -------- Jogador 1 (placar de cima) --------
        y1 = 215
        nome_surf_1 = fonte.render(f"{nome1}", True, cor1)
        score_surf_1 = fonte.render(f"{score1}", True, BRANCO)
        
        total_w1 = nome_surf_1.get_width() + 8 + score_surf_1.get_width()
        x1 = PLACAR_X + (PLACAR_LARGURA - total_w1) // 2

        tela.blit(nome_surf_1, (x1, y1))
        tela.blit(score_surf_1, (x1 + nome_surf_1.get_width() + 8, y1))


        # -------- Jogador 2 (placar de baixo) --------
        y2 = 250
        nome_surf_2 = fonte.render(f"{nome2}", True, cor2)
        score_surf_2 = fonte.render(f"{score2}", True, BRANCO)

        total_w2 = nome_surf_2.get_width() + 8 + score_surf_2.get_width()
        x2 = PLACAR_X + (PLACAR_LARGURA - total_w2) // 2

        tela.blit(nome_surf_2, (x2, y2))
        tela.blit(score_surf_2, (x2 + nome_surf_2.get_width() + 8, y2))


        # --- MENSAGENS DE "BATEU" (MODIFICADO) ---
        # Fonte um pouco maior para o aviso
        fonte_aviso = pygame.font.SysFont("Arial", 30, bold=True)

        if not player1.vivo:
            # Texto Branco
            msg = fonte_aviso.render(f"{nome1} BATEU!", True, BRANCO)
            # Centraliza no eixo X
            msg_x = WIDTH // 2 - msg.get_width() // 2
            # Posição Y no topo (nuvens)
            msg_y = 30 
            tela.blit(msg, (msg_x, msg_y))
        
        if not player2.vivo:
            # Texto Branco
            msg = fonte_aviso.render(f"{nome2} BATEU!", True, BRANCO)
            # Centraliza no eixo X
            msg_x = WIDTH // 2 - msg.get_width() // 2
            # Posição Y um pouco abaixo do aviso do P1 para não encavalar
            msg_y = 35
            tela.blit(msg, (msg_x, msg_y))
        # ------------------------------------------

        pygame.display.update()
        CLOCK.tick(FPS)

    
    if score1 > score2:
        pygame.mixer.music.stop()

        return nome1, score1, score2
    elif score2 > score1:
        pygame.mixer.music.stop()

        return nome2, score1, score2
    else:
        pygame.mixer.music.stop()

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
                    return 
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

# ---------------- MAIN ----------------
def main():
    while True:

        tela_menu()

        n1, n2 = tela_nomes_dupla()

        c1, c2 = tela_selecao_cavalos(n1, n2)
        
        vencedor_nome, s1, s2 = jogo_multiplayer(n1, n2, c1, c2)
        
        tela_vencedor(vencedor_nome, s1, s2)

if __name__ == "__main__":
    main()
