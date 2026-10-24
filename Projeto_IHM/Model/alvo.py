class Alvo:

    def __init__(self, x, y, raio=2):
        self.x = x
        self.y = y
        self.raio = raio
        self.atingido = False

    def foi_atingido(self): return self.atingido
    def modifica_estado(self,estado): self.atingido = estado