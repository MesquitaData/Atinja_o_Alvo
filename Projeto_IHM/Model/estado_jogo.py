
import json
import os
import time


class EstatisticasJogo:
    def __init__(self, arquivo="dados_jogo.json"):
        self.arquivo = arquivo
        self.historico = self.carregar_dados()

        self.jogo_atual = None
        self.nivel_atual = 1
        self.tentativas = 0
        self.inicio_nivel = None

    def carregar_dados(self):
        if not os.path.exists(self.arquivo):
            return {}

        try:
            with open(self.arquivo, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            # Converte o formato antigo para preservar os registros existentes.
            if "niveis" in dados:
                dados = {"Jogo 1": {"niveis": dados["niveis"]}}

            return dados

        except (json.JSONDecodeError, OSError):
            return {}

    def salvar_dados(self):
        with open(self.arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(
                self.historico,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    def iniciar_jogo(self):
        numero_jogo = len(self.historico) + 1
        self.jogo_atual = f"Jogo {numero_jogo}"

        self.historico[self.jogo_atual] = {"niveis": []}

        self.nivel_atual = 1
        self.tentativas = 0
        self.inicio_nivel = time.monotonic()

        self.salvar_dados()

    def registrar_tentativa(self):
        if self.jogo_atual is not None:
            self.tentativas += 1

    def concluir_nivel(self):
        if self.jogo_atual is None or self.inicio_nivel is None:
            return

        tempo_jogado = time.monotonic() - self.inicio_nivel

        registro = {
            "nivel": self.nivel_atual,
            "tentativas": self.tentativas,
            "tempo_jogado": f"{round(tempo_jogado, 2)} segundos"
        }

        self.historico[self.jogo_atual]["niveis"].append(registro)
        self.salvar_dados()

        self.nivel_atual += 1
        self.tentativas = 0
        self.inicio_nivel = time.monotonic()