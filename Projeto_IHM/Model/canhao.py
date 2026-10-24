import math
class Canhao:
    def __init__(self, x, y):
        # Posições físicas do canhão e inicializações
        self.x = x
        self.y = y
        self.angulo = 10
        self.velocidade_inicial = 10
        self.comprimento = 2.0  # Comprimento do canhão em metros

    def aumentar_angulo(self,incremento):
        if self.angulo < 90:
            self.angulo += incremento

    def diminuir_angulo(self,decremento):
        if self.angulo > 0:
            self.angulo -= decremento

    def aumentar_velocidade(self,valor):
        if self.velocidade_inicial < 100:
            self.velocidade_inicial += valor

    def diminuir_velocidade(self,valor):
        if self.velocidade_inicial > 0:
            self.velocidade_inicial -= valor

    def obter_ponta(self):
        angulo_rad = math.radians(self.angulo)  # converte o ângulo de graus para radiano

        # Obtem a posição (x,y) da ponta do canhão
        ponta_x = (self.x + self.comprimento * math.cos(angulo_rad))
        ponta_y = (self.y + self.comprimento * math.sin(angulo_rad))

        return ponta_x, ponta_y

    def obter_componentes_velocidade(self):
        angulo_rad = math.radians(self.angulo)
        vx = (self.velocidade_inicial * math.cos(angulo_rad))
        vy = (self.velocidade_inicial * math.sin(angulo_rad))

        return vx, vy