'''
    > Classe que instanciará objetos do tipo Projetil
    > que terão atributos seus atributos posicionais
    > além do método que calcula os pontos de sua trajetória
    > de lançamento.
'''

class Projetil:
    def __init__(self, x, y, vx, vy):
        self.x_ini = x  # Seta as posições iniciais
        self.y_ini = y

        self.x = x  # Seta as coordenadas atuais do projétil
        self.y = y

        self.vx_ini = vx  # Seta as velocidades iniciais
        self.vy_ini = vy

        self.vx = vx  # Velocidades instantaneas do projétil
        self.vy = vy

        self.tempo_voo = 0.0 # Quarda o tempo total de voo do projétil

        self.altura_maxima = y

        self.alcance = 0.0 # Quarda o alcance horizontal total do lançamento

        self.ativo = True # Estado do projétil

        self.trajetoria = [(x, y)]  # Histórico dos pontos da trajetória do projétil

    def atualizar(self, delta_tempo, gravidade):
        if not self.ativo:
            return

        # Atualiza o tempo total de voo do projétil
        self.tempo_voo += delta_tempo
        tempo_instantaneo = self.tempo_voo

        # Equação do movimento horizontal(Movimento retilíneo uniforme(x))
        self.x = (self.x_ini + self.vx_ini * tempo_instantaneo)

        # Equação do movimento vertical(Movimento retilíneo vertical(y) variando com a gravidade)
        self.y = (self.y_ini + self.vy_ini * tempo_instantaneo - 0.5 * gravidade * tempo_instantaneo ** 2)

        # Equação da velocidade vertical(Velocidade variante com a gravidade)
        self.vy = (self.vy_ini - gravidade * tempo_instantaneo)

        # A velocidade horizontal é constante!
        self.vx = self.vx_ini

        # Guarda o valor da maior altura registrada durante o lançamento!
        if self.y > self.altura_maxima:
            self.altura_maxima = self.y

        # Só por protocolo, pois x_ini é sempre ZERO(Poderia ser que em próximos estágios venha a precisar!)
        self.alcance = (self.x - self.x_ini)

        # Guarda o ponto da trajetória
        self.trajetoria.append((self.x, self.y))

    def desativar(self): self.ativo = False
    def get_estado(self): return self.ativo