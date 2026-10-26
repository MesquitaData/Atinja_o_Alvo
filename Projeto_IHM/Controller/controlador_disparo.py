import pygame
from Model.estado_jogo import EstatisticasJogo
from Model.jogo import Jogo

class JogoController:
    def __init__(self, view, interpretador):
        self.view = view
        self.interpretador = interpretador
        self.estatisticas = EstatisticasJogo()
        self.jogo = self.interpretador.get_jogo()
        self.acerto_processado = False

        # O interpretador chama este callback a cada disparo.
        self.interpretador.ao_disparar = (
            self.estatisticas.registrar_tentativa)

    def iniciar_nova_partida(self):
        self.estatisticas.iniciar_jogo()
        self.configurar_nivel(1)

    def inserir_parametros(self):
        jogo = self.interpretador.get_jogo()
        valores = self.view.obter_valores_campos()

        if valores is None:
            self.view.mostrar_mensagem(
                "Preencha os campos com valores numericos validos."
            )
            return False

        angulo, velocidade, gravidade = valores

        # Valida os parâmetros
        if not 0 <= angulo <= 90:
            self.view.mostrar_mensagem(
                "O angulo deve estar entre 0 e 90 graus."
            )
            return False

        if velocidade <= 0 or gravidade <= 0:
            self.view.mostrar_mensagem(
                "Velocidade e gravidade devem ser positivas."
            )
            return False

        # O ângulo é editável em todos os níveis
        jogo.canhao.angulo = angulo

        # A velocidade é editável a partir do nível 2
        if jogo.nivel >= 2:
            jogo.canhao.velocidade_inicial = velocidade

        # A gravidade é editável a partir do nível 3
        if jogo.nivel >= 3:
            jogo.gravidade = gravidade

        self.view.atualizar_campos(jogo)

        return True

    def processar_eventos(self):
        jogo = self.interpretador.get_jogo()
        for evento in pygame.event.get():
            self.view.processar_evento_campo(evento, jogo)
            if evento.type == pygame.QUIT: return False
            if not jogo.disparando:
                resultado_editor = self.view.processar_evento_editor(evento)
                if resultado_editor == "EXECUTAR":
                    if not self.inserir_parametros():  # Aplica os valores dos campos antes do disparo
                        continue

                    codigo = self.view.obter_codigo()
                    resultado = self.interpretador.executar(codigo)

                    if resultado is not None:
                        self.view.mostrar_mensagem(resultado)

                    continue

            if self.view.botao_reiniciar_click(evento):
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

        # Atualiza a simulação e verifica se houve acerto
        alvo_atingido = jogo.atualizar(dt)

        if alvo_atingido and not self.acerto_processado:
            self.acerto_processado = True

            self.estatisticas.concluir_nivel()

            # Encerra a execução anterior do interpretador
            self.interpretador.executando = False
            self.interpretador.comandos = []
            self.interpretador.indice_atual = 0
            self.interpretador.bloco_repita = []
            self.interpretador.indice_bloco = 0
            self.interpretador.executando_repita = False

            # Avança o nível e configura seus parâmetros
            self.avancar_nivel()

            # Prepara o jogo para o próximo disparo
            jogo.reiniciar_com_novo_alvo()

            self.view.atualizar_campos_nivel(jogo.nivel)
            self.view.atualizar_campos(jogo)

            # Libera o processamento de um próximo acerto.
            # O próximo acerto só será detectado após novo disparo.
            self.acerto_processado = False

            return

        # Se o disparo terminou sem acertar, permite uma nova tentativa
        if jogo.atingiu_solo():
            self.view.reiniciar_camera()

            # Libera o processamento do próximo acerto
            self.acerto_processado = False

        # Continua a execução normal do interpretador
        self.interpretador.atualizar()
        self.view.atualizar_campos(jogo)

    def configurar_nivel(self, nivel):
        self.jogo.nivel = nivel

        if nivel == 1:
            self.jogo.canhao.angulo = 10
            self.jogo.canhao.velocidade_inicial = 30
            self.jogo.gravidade = 9.81

        elif nivel == 2:
            self.jogo.canhao.angulo = 10
            self.jogo.canhao.velocidade_inicial = 10
            self.jogo.gravidade = 9.81

        else:
            self.jogo.canhao.angulo = 10
            self.jogo.canhao.velocidade_inicial = 10
            self.jogo.gravidade = 9.81

        self.view.atualizar_campos_nivel(nivel)
        self.view.atualizar_campos(self.jogo)
        self.view.mostrar_mensagem_nivel(nivel)

    def avancar_nivel(self):
        self.configurar_nivel(self.jogo.nivel+1)