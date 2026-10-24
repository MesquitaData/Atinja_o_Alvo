import pygame
from Model.canhao import Canhao
from Model.alvo import Alvo
from Model.jogo import Jogo
from View.gameView import JogoView
from Controller.controlador_disparo import JogoController
from Controller.comandos_logicos import Interpretador

LARGURA = 1340
ALTURA = 740

pygame.init()

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption(
    "Atinja o Alvo - Lançamento Oblíquo"
)

clock = pygame.time.Clock()

jogo = Jogo(LARGURA, ALTURA)

canhao = Canhao(0, 0)
jogo.configurar_canhao(canhao)

alvo = Alvo(x=80, y=2, raio=2)
jogo.configurar_alvo(alvo)

view = JogoView(tela)
interpretador = Interpretador(jogo)
controller = JogoController(view, interpretador)

rodando = True
tela_atual = "INICIAL"

# Inicializa os campos uma única vez.
view.inicializar_campos(jogo)


while rodando:
    dt = clock.tick(60) / 1000
    if tela_atual == "INICIAL":
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                break
            resultado = view.processar_evento_tela_inicial(evento)

            if resultado == "INICIAR":
                controller.iniciar_nova_partida()
                tela_atual = "JOGO"

            elif resultado == "TUTORIAL":
                tela_atual = "TUTORIAL"

        if rodando and tela_atual == "INICIAL":
            view.desenhar_tela_inicial()

    elif tela_atual == "TUTORIAL":
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                break

            resultado = view.processar_evento_tutorial(
                evento
            )

            if resultado == "VOLTAR":
                tela_atual = "INICIAL"

            elif resultado == "INICIAR":
                controller.iniciar_nova_partida()
                tela_atual = "JOGO"

        if rodando and tela_atual == "TUTORIAL":
            view.desenhar_tutorial()

    elif tela_atual == "JOGO":
        rodando = controller.processar_eventos()
        if not rodando:
            break

        controller.atualizar(dt)
        view.desenhar(jogo)
        view.desenhar_campos()
        view.desenhar_mensagem()
    pygame.display.update()
pygame.quit()