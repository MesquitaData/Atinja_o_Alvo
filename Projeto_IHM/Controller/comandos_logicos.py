from Model.alvo import Alvo
from Model.canhao import Canhao
from Model.projetil import Projetil
import re

class Interpretador:

    def __init__(self, jogo):
        self.jogo = jogo
        self.ao_disparar = None

        # Lista de comandos do programa
        self.comandos = []

        # Índice do comando atual
        self.indice_atual = 0

        # Estado da execução
        self.executando = False

        # Estado do bloco REPITA ATE ATINGIR
        self.bloco_repita = []
        self.indice_bloco = 0
        self.executando_repita = False

    def get_jogo(self):
        return self.jogo

    def parar_execucao(self):
        """Interrompe a execução e limpa o estado do interpretador."""
        self.executando = False
        self.executando_repita = False
        self.comandos.clear()
        self.bloco_repita.clear()
        self.indice_atual = 0
        self.indice_bloco = 0

    def comando_valido(self, comando):
        """Verifica se o comando possui uma sintaxe reconhecida."""

        comando = comando.strip().upper().replace(" ", "")

        numero = r"-?\d+(?:[.,]\d+)?"

        padroes = [
            r"ANGULO=" + numero,
            r"ANGULO\+\+",
            r"ANGULO--",
            r"ANGULO\+=" + numero,
            r"ANGULO-=" + numero,
            r"ANGULO=ANGULO\+" + numero,
            r"ANGULO=ANGULO-" + numero,

            r"VELOCIDADE=" + numero,
            r"VELOCIDADE\+\+",
            r"VELOCIDADE--",
            r"VELOCIDADE\+=" + numero,
            r"VELOCIDADE-=" + numero,
            r"VELOCIDADE=VELOCIDADE\+" + numero,
            r"VELOCIDADE=VELOCIDADE-" + numero,

            r"GRAVIDADE=" + numero,
        ]

        if comando in ("DISPARAR", "REINICIAR"):
            return True

        return any(
            re.fullmatch(padrao, comando)
            for padrao in padroes
        )

    def executar(self, codigo):
        """Valida e prepara o programa antes de executá-lo."""
        linhas = codigo.splitlines()
        pilha_blocos = []

        # Primeira passagem: validação do programa inteiro.
        for indice, linha in enumerate(linhas, start=1):
            comando = linha.strip().upper()

            if not comando:
                continue

            if comando == "REPITA ATE ATINGIR":
                pilha_blocos.append("REPITA ATE ATINGIR")
                continue

            if comando.startswith("REPITA"):
                quantidade = comando.replace("REPITA", "", 1).strip()

                if not quantidade.isdigit():
                    return f"Erro na Linha {indice}: Quantidade de repetição inválida!"

                pilha_blocos.append("REPITA")
                continue

            if comando == "FIM":
                if not pilha_blocos:
                    return f"Erro na Linha {indice}: FIM sem bloco correspondente!"

                pilha_blocos.pop()
                continue

            if not self.comando_valido(comando):
                return f"Erro na Linha {indice}: O comando {linha.strip()} é inválido!"

        if pilha_blocos:
            return "Erro: existe um bloco REPITA sem FIM."

        # Segunda passagem: prepara a execução.
        self.parar_execucao()
        self.jogo.alvo_foi_atingido = False

        i = 0

        while i < len(linhas):
            comando = linhas[i].strip().upper()

            if not comando:
                i += 1
                continue

            if comando == "REPITA ATE ATINGIR":
                i = self.interpretar_repita_ate_atingir(
                    linhas, i
                )
                continue

            elif comando.startswith("REPITA"):
                i = self.interpretar_repeticao(
                    linhas, i
                )
                continue

            else:
                self.comandos.append(comando)
                i += 1

        self.indice_atual = 0
        self.executando = True
        return None

    def interpretar_repeticao(self, linhas, indice_inicio):
        """Expande um bloco REPITA N em comandos sequenciais."""

        comando = linhas[indice_inicio].strip().upper()
        texto_quantidade = comando.replace(
            "REPITA", "", 1
        ).strip()

        try:
            quantidade = int(texto_quantidade)

            if quantidade < 0:
                raise ValueError

        except ValueError:
            print("Quantidade de repetição inválida:",
                  texto_quantidade)
            return indice_inicio + 1

        bloco = []
        i = indice_inicio + 1

        # Procura o FIM do bloco
        while i < len(linhas):
            linha = linhas[i].strip()

            if linha.upper() == "FIM":
                break

            if linha:
                bloco.append(linha.upper())

            i += 1

        if i >= len(linhas):
            print("Erro: bloco REPITA sem FIM.")
            return len(linhas)

        # Adiciona os comandos à fila pela quantidade solicitada
        for _ in range(quantidade):
            self.comandos.extend(bloco)

        return i + 1

    """Armazena o bloco REPITA ATE ATINGIR sem iniciá-lo imediatamente."""
    def interpretar_repita_ate_atingir(self, linhas, indice_inicio):
        bloco = []
        i = indice_inicio + 1

        while i < len(linhas):
            linha = linhas[i].strip()

            if linha.upper() == "FIM":
                break

            if linha:
                bloco.append(linha.upper())

            i += 1

        if i >= len(linhas):
            return len(linhas)

        self.bloco_repita = bloco
        self.indice_bloco = 0

        # Não ativar a repetição durante a leitura do programa.
        self.executando_repita = False

        return i + 1

    """Executa gradualmente os comandos na ordem em que foram escritos."""
    def atualizar(self):
        if not self.executando:
            return

        # Interrompe a execução se o alvo foi atingido.
        if self.jogo.alvo_foi_atingido:
            self.parar_execucao()
            return

        # Aguarda o projétil terminar a trajetória antes de executar
        # o próximo comando.
        if (
                self.jogo.projetil is not None
                and self.jogo.projetil.get_estado()
        ):
            return

        # 1. Executa os comandos anteriores ao bloco de repetição.
        if self.indice_atual < len(self.comandos):
            comando = self.comandos[self.indice_atual].strip().upper()

            resultado = self.executar_comando(comando)

            if resultado is not None:
                self.mensagem_erro = resultado
                self.parar_execucao()
                return

            self.indice_atual += 1
            return

        # 2. Só inicia a repetição depois dos comandos anteriores.
        if self.bloco_repita:
            self.executando_repita = True

        # 3. Executa o bloco REPITA ATE ATINGIR.
        if self.executando_repita:
            if not self.bloco_repita:
                self.parar_execucao()
                return

            if self.indice_bloco >= len(self.bloco_repita):
                self.indice_bloco = 0
                return

            comando = self.bloco_repita[self.indice_bloco].strip().upper()
            resultado = self.executar_comando(comando)

            if resultado is not None:
                self.mensagem_erro = resultado
                self.parar_execucao()
                return

            self.indice_bloco += 1
            return

        # 4. Finaliza quando não houver mais comandos ou blocos.
        self.executando = False

    def executar_bloco_ate_atingir(self, bloco):
        """Executa comandos de um bloco até um disparo ou acerto."""

        if self.jogo.alvo_foi_atingido:
            self.parar_execucao()
            return

        if (
            self.jogo.projetil is not None
            and self.jogo.projetil.get_estado()
        ):
            return

        for comando in bloco:
            if self.jogo.alvo_foi_atingido:
                self.parar_execucao()
                return

            self.executar_comando(comando)

            if comando.strip().upper() == "DISPARAR":
                return

    def executar_comando(self, comando):
        """Identifica e executa cada comando."""

        comando = comando.strip().upper()

        if comando.startswith("ANGULO"):
            if not self.jogo.parametro_permitido("ANGULO"):
                return "O ângulo não pode ser alterado neste nível."
            self.interpretar_angulo(comando)

        elif comando.startswith("VELOCIDADE"):
            if not self.jogo.parametro_permitido("VELOCIDADE"):
                return "A velocidade não pode ser alterada neste nível."
            self.interpretar_velocidade(comando)

        elif comando.startswith("GRAVIDADE"):
            if not self.jogo.parametro_permitido("GRAVIDADE"):
                return "A gravidade não pode ser alterada neste nível."
            self.interpretar_angulo(comando)

        elif comando == "DISPARAR":
            disparou = self.jogo.disparar()
            if (disparou and self.ao_disparar) is not None: return self.ao_disparar()

        elif comando == "REINICIAR":
            self.jogo.reiniciar()

        else:
            return f"Comando inválido: {comando}"

    def interpretar_angulo(self, comando):
        comando = comando.replace(" ", "")

        if comando.startswith("ANGULO="):
            valor = comando.replace("ANGULO=", "", 1)

            try:
                self.jogo.canhao.angulo = float(
                    valor.replace(",", ".")
                )
            except ValueError:
                return f"Valor inválido para o ângulo!"

        elif comando == "ANGULO++":
            self.jogo.canhao.aumentar_angulo(1)

        elif comando == "ANGULO--":
            self.jogo.canhao.diminuir_angulo(1)

        elif comando.startswith("ANGULO+="):
            valor = comando.replace("ANGULO+=", "", 1)

            try:
                incremento = float(valor.replace(",", "."))
                self.jogo.canhao.aumentar_angulo(incremento)
            except ValueError:
                return f"Incremento de ângulo inválido!"

        elif comando.startswith("ANGULO-="):
            valor = comando.replace("ANGULO-=", "", 1)

            try:
                decremento = float(valor.replace(",", "."))
                self.jogo.canhao.diminuir_angulo(decremento)
            except ValueError:
                return f"Decremento de ângulo inválido!"

        elif comando.startswith("ANGULO=ANGULO+"):
            valor = comando.replace(
                "ANGULO=ANGULO+", "", 1
            )

            try:
                incremento = float(valor.replace(",", "."))
                self.jogo.canhao.aumentar_angulo(incremento)
            except ValueError:
                return f"Incremento de ângulo inválido!"

        elif comando.startswith("ANGULO=ANGULO-"):
            valor = comando.replace(
                "ANGULO=ANGULO-", "", 1
            )

            try:
                decremento = float(valor.replace(",", "."))
                self.jogo.canhao.diminuir_angulo(decremento)
            except ValueError:
                return f"Decremento de ângulo inválido!"

        else:
            return f"Comando inválido!"
        return None

    def interpretar_velocidade(self, comando):
        comando = comando.strip().upper().replace(" ", "")

        try:
            if comando == "VELOCIDADE++":
                self.jogo.canhao.aumentar_velocidade(1)

            elif comando == "VELOCIDADE--":
                self.jogo.canhao.diminuir_velocidade(1)

            # Verificar as expressões compostas antes da atribuição simples.
            elif comando.startswith("VELOCIDADE=VELOCIDADE+"):
                valor = comando.replace(
                    "VELOCIDADE=VELOCIDADE+", "", 1
                )
                incremento = float(valor.replace(",", "."))
                self.jogo.canhao.aumentar_velocidade(incremento)

            elif comando.startswith("VELOCIDADE=VELOCIDADE-"):
                valor = comando.replace(
                    "VELOCIDADE=VELOCIDADE-", "", 1
                )
                decremento = float(valor.replace(",", "."))
                self.jogo.canhao.diminuir_velocidade(decremento)

            elif comando.startswith("VELOCIDADE+="):
                valor = comando.replace("VELOCIDADE+=", "", 1)
                incremento = float(valor.replace(",", "."))
                self.jogo.canhao.aumentar_velocidade(incremento)

            elif comando.startswith("VELOCIDADE-="):
                valor = comando.replace("VELOCIDADE-=", "", 1)
                decremento = float(valor.replace(",", "."))
                self.jogo.canhao.diminuir_velocidade(decremento)

            elif comando.startswith("VELOCIDADE="):
                valor = comando.replace("VELOCIDADE=", "", 1)
                self.jogo.canhao.velocidade_inicial = float(
                    valor.replace(",", ".")
                )

            else:
                return f"Comando de velocidade inválido: {comando}"

        except ValueError:
            return f"Valor de velocidade inválido: {comando}"

        return None

    def interpretar_gravidade(self, comando):
        comando = comando.replace(" ", "")

        if not comando.startswith("GRAVIDADE="):
            return f"Comando inválido para gravidade!"

        valor = comando.replace("GRAVIDADE=", "", 1)

        try:
            gravidade = float(valor.replace(",", "."))

            if gravidade <= 0:
                return f"A gravidade deve ser maior que zero!"

            self.jogo.GRAVIDADE = gravidade

        except ValueError:
            return f"Valor inválido para a gravidade!"

        return None