# Hipismo Runner Multiplayer

Um jogo de corrida infinita (endless runner) competitivo em tela dividida, desenvolvido em Python com a biblioteca Pygame. Dois jogadores escolhem seus cavalos e competem simultaneamente para ver quem sobrevive por mais tempo desviando dos obstáculos!

---

## Vídeo de Apresentação

    #link do jogo 

---

## Membros do Grupo

* [Luka Cione Buchviser]
* [João Moraes Gutierrez Estevez]
* [Tadeu Henrique Brostowicz Martins]

---

## Uso de Inteligência Artificial

Para o desenvolvimento deste projeto, utilizamos a ferramenta institucional de IA generativa como assistente de programação (em formato pair programming).

A ideia original do jogo, a lógica base de física (gravidade e pulo) e os sprites foram definidos pelo grupo. A IA foi consultada para as seguintes tarefas de expansão e refatoração:

    Refatoração para Multiplayer (Split-Screen): Ajudou a transformar as variáveis globais de posição (como o "chão") em atributos de classe, permitindo instanciar dois jogos simultâneos (Jogador 1 em cima, Jogador 2 embaixo) na mesma janela.

    Sistema de Menus e Fluxo: Auxiliou na lógica de transição entre telas (Menu Inicial -> Inserção de Nomes -> Seleção de Cavalos -> Jogo), criando funções modulares para cada etapa.

Declaração: Nenhuma função principal foi "100% gerada" sem entendimento. Todas as sugestões da IA (especialmente na lógica de classes e loops de eventos) foram revisadas, testadas e integradas manualmente pelo grupo. A lógica core do jogo permanece autoral.

---

## Como Rodar o Jogo

Para jogar, você precisará ter o Python 3 e a biblioteca Pygame instalados em seu computador.
1. Instalação de Dependências

Se você ainda não tem o Pygame, pode instalá-lo facilmente usando o pip. Abra seu terminal ou prompt de comando e digite:
    pip install pygame

2. Executando o Jogo
Navegue até a pasta do projeto e execute o arquivo principal:
    python main.py

3. Controles

    Jogador 1 (Tela Superior):

        W: Pular

        A/S (no menu): Trocar seleção

    Jogador 2 (Tela Inferior):

        Seta CIMA: Pular

        Setas CIMA/BAIXO (no menu): Trocar seleção

    Geral:

        ESC: Sair do jogo

        R: Reiniciar (na tela de vencedor)