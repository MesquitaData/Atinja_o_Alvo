import pygame
from Model.estado_jogo import EstatisticasJogo
from Model.jogo import Jogo

class JogoController:
    def __init__(self, view, interpretador):
        self.view = view
        self.interpretador = interpretador
        self.estatisticas = EstatisticasJogo()

        # O interpretador chama este callback a cada disparo.
        self.interpretador.ao_disparar = (
            self.estatisticas.registrar_tentativa)

    def iniciar_nova_partida(self):
        self.estatisticas.iniciar_jogo()

    def inserir_parametros(self):
        jogo = self.interpretador.get_jogo()
        valores = self.view.obter_valores_campos()

        if valores is None:
            return

        angulo, velocidade, gravidade = valores
        jogo.canhao.angulo = angulo
        jogo.canhao.velocidade_inicial = velocidade
        jogo.gravidade = gravidade

    def processar_eventos(self):
        jogo = self.interpretador.get_jogo()

        for evento in pygame.event.get():
            self.view.processar_evento_campo(evento, jogo)
            resultado_editor = self.view.processar_evento_editor(evento)

            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if self.view.botao_inserir.collidepoint(evento.pos):
                        self.inserir_parametros()

            if resultado_editor == "EXECUTAR":
                codigo = self.view.obter_codigo()
                resultado = self.interpretador.executar(codigo)
                if resultado is not None:
                    self.view.mostrar_mensagem(resultado)
                continue

            elif resultado_editor == "REINICIAR":
                jogo.reiniciar()
                self.interpretador.executando = False
                self.interpretador.comandos = []
                self.interpretador.indice_atual = 0
                self.interpretador.bloco_repita = []
                self.interpretador.indice_bloco = 0
                self.interpretador.executando_repita = False
                self.view.limpar_codigo()
                self.view.reiniciar_campos()
                continue

        return True

    def atualizar(self, dt):
        jogo = self.interpretador.get_jogo()
        alvo_atingido = jogo.atualizar(dt)
        parou_lancamento = jogo.atingiu_solo()
        valores = self.view.obter_valores_campos()

        if valores is not None:
            angulo, velocidade, gravidade = valores
            jogo.canhao.angulo = angulo
            jogo.canhao.velocidade_inicial = velocidade
            jogo.gravidade = gravidade

        if alvo_atingido:
            self.view.modo_camera = "visao_geral"
            self.estatisticas.concluir_nivel()
            self.interpretador.executando = False
            self.interpretador.comandos = []
            self.interpretador.indice_atual = 0

        else:
            if parou_lancamento: self.view.reiniciar_camera()
            self.interpretador.atualizar()
            self.view.atualizar_campos(jogo)