from .projetil import Projetil
from .alvo import Alvo
from .canhao import Canhao
from random import randint
import pygame
class Jogo:

    def __init__(self, largura, altura):
        self.gravidade = 9.81
        self.largura = largura
        self.altura = altura
        self.canhao = None
        self.projetil = None
        self.alvo = None
        self.disparando = False
        self.simulacao_finalizada = False
        self.alvo_foi_atingido = False
        self.nivel = 1

    def configurar_canhao(self, canhao):
        self.canhao = canhao

    def parametro_permitido(self, parametro):
        permissoes = {
            1: ["ANGULO"],
            2: ["ANGULO", "VELOCIDADE"],
        }
        if self.nivel >= 3:
            return parametro in ["ANGULO", "VELOCIDADE", "GRAVIDADE"]
        return parametro in permissoes[self.nivel]

    def configurar_alvo(self, alvo):
        self.alvo = alvo

    def disparar(self):

        if self.canhao is None:  # Verifica se existe canhão
            return False

        # Impede disparo enquanto existe projétil ativo/Ainda não finalizou o lançamento/N tocou o chão
        if (self.projetil is not None and self.projetil.get_estado()):
            return False

        # Obtém componentes da velocidade
        vx, vy = (self.canhao.obter_componentes_velocidade())

        # Cria o projetil
        self.projetil = Projetil(0, 0, vx, vy)

        # Atualiza estado
        self.disparando = True
        self.simulacao_finalizada = False
        return True

    '''
    def reiniciar_com_novo_alvo(self):
        n = randint(30, 150) # Sorteia uma distância inteira entre 30 m e 150 m
        nova_posicao_x = n - n%10

        # Remove o projétil anterior
        self.projetil = None

        # Reinicia os estados da simulação
        self.disparando = False
        self.simulacao_finalizada = False

        # Cria o alvo em uma nova posição
        self.alvo.x = nova_posicao_x
    '''

    def reiniciar_com_novo_alvo(self):
        if self.alvo is None:
            return

        n = randint(30, 150)
        nova_posicao_x = n - n % 10

        self.projetil = None
        self.disparando = False
        self.simulacao_finalizada = False
        self.alvo_foi_atingido = False

        self.alvo.x = nova_posicao_x
        self.alvo.modifica_estado(False)

    def verificar_colisao_alvo(self):

        # Verificando se ou o alvo ou o projétil não existe, pois só há colisão se ambos existirem
        if (self.projetil is None or self.alvo is None):
            return False

        dx = (self.projetil.x - self.alvo.x)
        dy = (self.projetil.y - self.alvo.y)

        distancia = (dx ** 2 + dy ** 2) ** 0.5 # Calcula a distância entre o centro do projétil ao do alvo
        raio_projetil = 1

        # Retorna True se essa distância for menor ou no máximo igual a soma dos raios
        return distancia <= (raio_projetil + self.alvo.raio)
    '''
    def atualizar(self, delta_tempo):
        if self.projetil is None:
            return False

        if not self.projetil.get_estado():
            return False

        self.projetil.atualizar(delta_tempo, self.gravidade)

        if self.verificar_colisao_alvo():
            self.alvo_foi_atingido = True
            self.alvo.modifica_estado(True)
            self.projetil.desativar()
            self.reiniciar_com_novo_alvo()
            return True

        if self.projetil.tempo_voo > 0 and self.projetil.y <= 0:
            self.projetil.y = 0
            self.projetil.desativar()
            self.disparando = False
            self.simulacao_finalizada = True
            # self.proximo_disparo = pygame.time.get_ticks() + 500

            return False
        return False
    '''
    '''
    def atualizar(self, delta_tempo):
        if self.projetil is None:
            return False

        if not self.projetil.get_estado():
            return False

        self.projetil.atualizar(delta_tempo, self.gravidade)

        # Verifica se o projétil atingiu o alvo
        if self.verificar_colisao_alvo():
            self.alvo_foi_atingido = True
            self.alvo.modifica_estado(True)

            self.projetil.desativar()
            self.disparando = False
            self.simulacao_finalizada = True

            # Informa ao Controller que houve um acerto
            return True

        # Verifica se o projétil atingiu o solo
        if self.projetil.tempo_voo > 0 and self.projetil.y <= 0:
            self.projetil.y = 0
            self.projetil.desativar()
            self.disparando = False
            self.simulacao_finalizada = True

            return False  # O disparo terminou, mas não houve acerto
        return False
    '''

    def atualizar(self, delta_tempo):
        if self.projetil is None:
            return False

        if not self.projetil.get_estado():
            return False

        self.projetil.atualizar(delta_tempo, self.gravidade)

        # O alvo foi atingido
        if self.verificar_colisao_alvo():
            self.alvo_foi_atingido = True
            self.alvo.modifica_estado(True)

            self.projetil.desativar()
            self.disparando = False
            self.simulacao_finalizada = True

            # O Controller tratará o acerto
            return True

        # O projétil atingiu o solo
        if self.projetil.tempo_voo > 0 and self.projetil.y <= 0:
            self.projetil.y = 0
            self.projetil.desativar()
            self.disparando = False
            self.simulacao_finalizada = True
            return False

        return False

    def atingiu_solo(self):
        if self.projetil is None: return False
        if self.projetil.tempo_voo > 0 and self.projetil.y <= 0: return True
        return False

    # Método que será chamado sempre que o usuário clicar no botão reiniciar
    def reiniciar(self):
        if self.canhao is not None:
            self.canhao.angulo = 10
            self.canhao.velocidade_inicial = 10

        self.projetil = None
        self.disparando = False
        self.simulacao_finalizada = False
        self.alvo_foi_atingido = False
        if self.alvo is not None: self.alvo.modifica_estado(False)

    def obter_dados_fisicos(self):
        if self.projetil is None:
            return {
                "tempo": 0,
                "altura_maxima": 0,
                "alcance": 0
            }

        return {
            "tempo":
                self.projetil.tempo_voo,
            "altura_maxima":
                self.projetil.altura_maxima,
            "alcance":
                self.projetil.alcance
        }