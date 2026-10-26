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
        valores = self.view.obter_valores_campos()
        if valores is None:
            return

        angulo, velocidade, gravidade = valores
        self.jogo.canhao.angulo = angulo

        if self.jogo.nivel >= 2:
            self.jogo.canhao.velocidade_inicial = velocidade

        if self.jogo.nivel >= 3:
            self.jogo.gravidade = gravidade

        self.view.atualizar_campos(self.jogo)

    def processar_eventos(self):
        jogo = self.interpretador.get_jogo()
        for evento in pygame.event.get():
            self.view.processar_evento_campo(evento, jogo)
            if evento.type == pygame.QUIT: return False
            if not jogo.disparando:
                resultado_editor = self.view.processar_evento_editor(evento)
                if resultado_editor == "EXECUTAR":
                    codigo = self.view.obter_codigo()
                    self.acerto_processado = False    # Permite contabilizar o próximo acerto
                    resultado = self.interpretador.executar(codigo)
                    if resultado is not None:
                        self.view.mostrar_mensagem(resultado)
                    continue

            elif self.view.botao_reiniciar_click(evento):
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

    '''
    def atualizar(self, dt):
        jogo = self.interpretador.get_jogo()
        alvo_atingido = jogo.atualizar(dt)
        parou_lancamento = jogo.atingiu_solo()
        valores = self.view.obter_valores_campos()

        if valores is not None:
            angulo, velocidade, gravidade = valores
            jogo.canhao.angulo = angulo

            if jogo.nivel >= 2:
                jogo.canhao.velocidade_inicial = velocidade

            if jogo.nivel >= 3:
                jogo.gravidade = gravidade
        
        if alvo_atingido:
            self.view.modo_camera = "visao_geral"
            if not self.acerto_processado:
                self.estatisticas.concluir_nivel()
                self.acerto_processado = True
                self.avancar_nivel()
            self.interpretador.executando = False
            self.interpretador.comandos = []
            self.interpretador.indice_atual = 0

        else:
            if parou_lancamento: self.view.reiniciar_camera()
            self.interpretador.atualizar()
            self.view.atualizar_campos(jogo)
        
        if alvo_atingido:
            self.view.modo_camera = "visao_geral"

            if not self.acerto_processado:
                self.acerto_processado = True

                self.estatisticas.concluir_nivel()

                self.avancar_nivel()
                jogo.reiniciar_com_novo_alvo()

                self.view.atualizar_campos_nivel(jogo.nivel)
                self.view.atualizar_campos(jogo)

            self.interpretador.executando = False
            self.interpretador.comandos = []
            self.interpretador.indice_atual = 0

        else:
            if parou_lancamento:
                self.view.reiniciar_camera()
            self.interpretador.atualizar()
            self.view.atualizar_campos(jogo)
    '''


    def atualizar(self, dt):
        jogo = self.interpretador.get_jogo()

        # Atualiza a simulação e verifica se houve acerto
        alvo_atingido = jogo.atualizar(dt)

        if alvo_atingido:
            if not self.acerto_processado:
                self.acerto_processado = True

                # Registra a conclusão do nível
                self.estatisticas.concluir_nivel()

                # Avança somente após acertar o alvo
                self.avancar_nivel()

                # Prepara o alvo para a próxima tentativa
                jogo.reiniciar_com_novo_alvo()

                # Atualiza a interface para o novo nível
                self.view.atualizar_campos_nivel(jogo.nivel)
                self.view.atualizar_campos(jogo)

            # Encerra a execução anterior do interpretador
            self.interpretador.executando = False
            self.interpretador.comandos = []
            self.interpretador.indice_atual = 0

            # Não processa outro comando neste mesmo quadro
            return

        # Se o disparo terminou sem acerto, permite tentar novamente
        if jogo.atingiu_solo():
            self.view.reiniciar_camera()

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