import pygame
import math
class JogoView:

    def __init__(self, tela):

        self.mensagem = ""
        self.tempo_mensagem = 0
        self.editor_ativo = False
        self.linhas_codigo = [""]
        self.linha_atual = 0
        self.cursor_posicao = 0

        # Dimensões da tela
        self.largura = tela.get_width()
        self.altura = tela.get_height()

        # Configurações do editor
        self.largura_editor = 300
        self.editor_x = self.largura - self.largura_editor - 10
        self.editor_y = 45

        # Configurações dos botões
        self.altura_botao = 30
        self.espaco_botoes = 12
        self.margem_inferior = 40

        # Camera do projétil
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_ativa = True
        self.camera_suavidade = 0.10
        self.modo_camera = "seguir"

        # Altura da caixa de código
        altura_editor = (
                self.altura
                - self.editor_y
                - self.altura_botao
                - self.espaco_botoes
                - self.margem_inferior
                - 70
        )

        self.editor_rect = pygame.Rect(
            self.editor_x,
            self.editor_y,
            self.largura_editor,
            altura_editor
        )

        # Botão EXECUTAR
        self.botao_executar = pygame.Rect(
            self.editor_x+10,
            self.editor_rect.bottom + self.espaco_botoes,
            130,
            self.altura_botao
        )

        # Botão REINICIAR
        self.botao_reiniciar = pygame.Rect(
            self.editor_x + 160,
            self.editor_rect.bottom + self.espaco_botoes,
            130,
            self.altura_botao
        )

        self.botao_iniciar = pygame.Rect(
            420,
            600,
            200,
            60
        )

        self.botao_tutorial = pygame.Rect(
            670,
            600,
            200,
            60
        )

        self.botao_voltar_tutorial = pygame.Rect(
            self.largura // 2 - 220,
            self.altura - 80,
            200,
            50
        )

        self.botao_iniciar_tutorial = pygame.Rect(
            self.largura // 2 + 60,
            self.altura - 80,
            200,
            50
        )

        self.tela = tela

        # Escala 1:8 pixels
        self.escala = 8
        self.escala_base = self.escala

        # Posição da origem do sistema físico na tela
        self.origem_x = 80
        self.chao_y = tela.get_height() - 80

        # Fontes
        self.fonte = pygame.font.SysFont("Arial", 20)
        self.fonte_titulo = pygame.font.SysFont("Arial", 18, bold=True)

        # Cores
        self.CEU = (135, 206, 235)
        self.CHÃO = (80, 160, 80)
        self.PRETO = (0, 0, 0)
        self.VERMELHO = (220, 50, 50)
        self.BRANCO = (255, 255, 255)
        self.AZUL = (50, 100, 220)
        self.CINZA = (100, 100, 100)
        self.VERDE = (0, 180, 0)

    def mundo_para_tela(self, x, y):
        tela_x = (
            self.origem_x
            + (x - self.camera_x) * self.escala
        )
        tela_y = (
            self.chao_y
            - (y - self.camera_y) * self.escala
        )

        return int(tela_x), int(tela_y)

    def atualizar_camera(self, jogo):
        projetil = jogo.projetil
        alvo = jogo.alvo

        if projetil is None:
            self.camera_x = 0.0
            self.camera_y = 0.0
            self.escala = self.escala_base
            self.modo_camera = "seguir"
            return

        if self.modo_camera == "seguir":

            self.escala = self.escala_base

            if alvo is not None and projetil.x <= alvo.x:
                return

            alvo_x = projetil.x - (
                    self.largura / 2 - self.origem_x
            ) / self.escala

            alvo_y = projetil.y - (
                    self.chao_y - self.altura / 2
            ) / self.escala

            self.camera_x += (
                                     alvo_x - self.camera_x
                             ) * self.camera_suavidade

            self.camera_y += (
                                     alvo_y - self.camera_y
                             ) * self.camera_suavidade

            # O eixo não desce abaixo da posição inicial
            self.camera_y = max(0.0, self.camera_y)

        elif self.modo_camera == "visao_geral":

            alvo = jogo.alvo

            if alvo is None:
                return

            # Coordenadas físicas dos dois pontos
            x1, y1 = alvo.x, alvo.y
            x2, y2 = projetil.x, projetil.y

            # Limites do enquadramento
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)

            margem = 70

            largura_mundo = max(max_x - min_x, 1.0)
            altura_mundo = max(max_y - min_y, 1.0)

            # Escala necessária para mostrar ambos os pontos
            escala_x = (
                               self.largura - 2 * margem
                       ) / largura_mundo

            escala_y = (
                               self.altura - 2 * margem
                       ) / altura_mundo

            escala_desejada = min(
                self.escala_base,
                escala_x,
                escala_y
            )

            # Evita zoom excessivo
            escala_desejada = max(0.5, escala_desejada)

            # Transição suave do zoom
            self.escala += (
                                   escala_desejada - self.escala
                           ) * 0.08

            # Centro entre o alvo e o ponto de queda
            meio_x = (x1 + x2) / 2
            meio_y = (y1 + y2) / 2

            camera_x_desejada = meio_x - (
                    self.largura / 2 - self.origem_x
            ) / self.escala

            camera_y_desejada = meio_y - (
                    self.chao_y - self.altura / 2
            ) / self.escala

            self.camera_x += (
                                     camera_x_desejada - self.camera_x
                             ) * 0.08

            self.camera_y += (
                                     camera_y_desejada - self.camera_y
                             ) * 0.08

            self.camera_y = max(0.0, self.camera_y)

    # ==========================================================
    # DESENHAR TUDO
    # ==========================================================
    def desenhar(self, jogo):

        self.atualizar_camera(jogo)

        # Céu
        self.tela.fill(self.CEU)

        # Chão
        self.desenhar_chao()

        # Eixo horizontal
        self.desenhar_eixo()

        # Canhão
        if jogo.canhao is not None:
            self.desenhar_canhao(jogo.canhao)

        # Trajetória
        if jogo.projetil is not None:
            self.desenhar_trajetoria(jogo.projetil)

            # Projétil
            self.desenhar_projetil(jogo.projetil)

        if jogo.alvo is not None:
            self.desenhar_alvo(jogo.alvo)

        self.desenhar_interface(jogo)
        self.desenhar_editor()

    def desenhar_chao(self):

        # Posição do nível do solo após o deslocamento da câmera
        _, chao_tela_y = self.mundo_para_tela(0, 0)

        # Desenha o solo somente na região abaixo dele
        if chao_tela_y < self.altura:
            inicio_y = max(0, chao_tela_y)

            pygame.draw.rect(
                self.tela,
                self.CHÃO,
                (
                    0,
                    inicio_y,
                    self.largura,
                    self.altura - inicio_y
                )
            )

    def desenhar_eixo(self):

        # Posição do chão no sistema de coordenadas da tela
        _, chao_tela_y = self.mundo_para_tela(0, 0)

        # Desenha o eixo horizontal somente se estiver visível
        if 0 <= chao_tela_y < self.altura:
            pygame.draw.line(
                self.tela,
                self.PRETO,
                (0, chao_tela_y),
                (self.largura, chao_tela_y),
                2
            )

        # Intervalo de distâncias visível na tela
        x_min = max(
            0,
            self.camera_x - self.origem_x / self.escala
        )

        x_max = (
                self.camera_x
                + (self.largura - self.origem_x) / self.escala
        )

        # Primeira e última marcações, de 10 em 10 metros
        inicio = int(x_min // 10) * 10
        fim = int(x_max // 10 + 1) * 10

        for distancia in range(inicio, fim + 1, 10):

            tela_x, _ = self.mundo_para_tela(distancia, 0)

            # Evita desenhar marcações fora da tela
            if not 0 <= tela_x < self.largura:
                continue

            if 0 <= chao_tela_y < self.altura:

                pygame.draw.line(
                    self.tela,
                    self.CINZA,
                    (tela_x, chao_tela_y - 5),
                    (tela_x, chao_tela_y + 5),
                    1
                )

                texto = self.fonte.render(
                    f"{distancia} m",
                    True,
                    self.PRETO
                )

                # Centraliza o texto na marcação
                texto_rect = texto.get_rect(
                    center=(tela_x, chao_tela_y + 20)
                )

                # Exibe o rótulo somente quando couber na tela
                if (
                        texto_rect.left >= 0
                        and texto_rect.right <= self.largura
                        and texto_rect.bottom <= self.altura
                ):
                    self.tela.blit(texto, texto_rect)

    # ==========================================================
    # CANHÃO
    # ==========================================================
    def desenhar_canhao(self, canhao):

        # ------------------------------------------------------
        # POSIÇÃO DO CENTRO DO CANHÃO
        # ------------------------------------------------------

        centro_x, centro_y = self.mundo_para_tela(
            canhao.x,
            canhao.y
        )

        # ------------------------------------------------------
        # BASE DO CANHÃO
        # ------------------------------------------------------

        pygame.draw.circle(
            self.tela,
            self.PRETO,
            (centro_x, centro_y),
            18
        )

        pygame.draw.circle(
            self.tela,
            self.CINZA,
            (centro_x, centro_y),
            12
        )

        # ------------------------------------------------------
        # TUBO DO CANHÃO
        # ------------------------------------------------------

        angulo_rad = math.radians(canhao.angulo)

        comprimento_pixels = canhao.comprimento * self.escala

        ponta_x = centro_x + comprimento_pixels * math.cos(angulo_rad)

        # IMPORTANTE:
        # Y da tela é invertido
        ponta_y = centro_y - comprimento_pixels * math.sin(angulo_rad)

        pygame.draw.line(
            self.tela,
            self.PRETO,
            (centro_x, centro_y),
            (int(ponta_x), int(ponta_y)),
            12
        )

        # ------------------------------------------------------
        # PONTA DO CANHÃO
        # ------------------------------------------------------

        pygame.draw.circle(
            self.tela,
            self.PRETO,
            (int(ponta_x), int(ponta_y)),
            7
        )

    def desenhar_projetil(self, projetil):

        x, y = self.mundo_para_tela(
            projetil.x,
            projetil.y
        )

        pygame.draw.circle(
            self.tela,
            self.VERMELHO,
            (x, y),
            8
        )

    def obter_valores_campos(self):
        try:
            angulo = int(self.campos["angulo"]["texto"].replace(",", "."))
            velocidade = int(self.campos["velocidade"]["texto"].replace(",", "."))
            gravidade = float(self.campos["gravidade"]["texto"].replace(",", "."))
            return angulo, velocidade, gravidade

        except ValueError:
            return None

    def atualizar_campos(self, jogo):
        if self.campo_ativo != "angulo":
            self.campos["angulo"]["texto"] = str(int(jogo.canhao.angulo))
        if self.campo_ativo != "velocidade":
            self.campos["velocidade"]["texto"] = str(int(jogo.canhao.velocidade_inicial))
        if self.campo_ativo != "gravidade":
            self.campos["gravidade"]["texto"] = str(jogo.gravidade)

    def desenhar_trajetoria(self, projetil):

        if len(projetil.trajetoria) < 2:
            return

        pontos = []

        for x, y in projetil.trajetoria:

            tela_x, tela_y = self.mundo_para_tela(x, y)

            # Só adiciona pontos que estejam razoavelmente
            # dentro da tela
            if (
                -100 < tela_x < self.tela.get_width() + 100
                and -100 < tela_y < self.tela.get_height() + 100
            ):
                pontos.append((tela_x, tela_y))

        if len(pontos) >= 2:

            pygame.draw.lines(
                self.tela,
                self.VERMELHO,
                False,
                pontos,
                2
            )

    def reiniciar_campos(self):
        self.campos["angulo"]["texto"] = "10"
        self.campos["velocidade"]["texto"] = "10"
        self.campos["gravidade"]["texto"] = "9.81"
        self.campo_ativo = None

    def inicializar_campos(self, jogo):
        self.campos = {
            "angulo": {
                "rect": pygame.Rect(190, 65, 70, 30),
                "texto": str(jogo.canhao.angulo if jogo.canhao else 45),
            },
            "velocidade": {
                "rect": pygame.Rect(190, 100, 70, 30),
                "texto": str(
                    jogo.canhao.velocidade_inicial
                    if jogo.canhao else 10
                ),
            },
            "gravidade": {
                "rect": pygame.Rect(190, 135, 70, 30),
                "texto": str(jogo.gravidade),
            },
        }

        rect_gravidade = self.campos["gravidade"]["rect"]
        self.botao_inserir = pygame.Rect(
            rect_gravidade.x-95,
            rect_gravidade.bottom + 15,
            90,
            45
        )

        self.campo_ativo = None

    def desenhar_campos(self):
        configuracoes = [
            ("angulo", "Ângulo:", "°"),
            ("velocidade", "Velocidade inicial:", "m/s"),
            ("gravidade", "Gravidade:", "m/s²"),
        ]

        for nome, rotulo, unidade in configuracoes:
            campo = self.campos[nome]
            rect = campo["rect"]

            texto_rotulo = self.fonte.render(
                rotulo, True, self.PRETO
            )
            self.tela.blit(
                texto_rotulo,
                (20, rect.y + 5)
            )

            cor_borda = (
                (40, 110, 220)
                if self.campo_ativo == nome
                else (100, 100, 100)
            )

            pygame.draw.rect(
                self.tela,
                (255, 255, 255),
                rect
            )

            pygame.draw.rect(
                self.tela,
                cor_borda,
                rect,
                2,
                border_radius=4
            )

            texto_valor = self.fonte.render(
                campo["texto"],
                True,
                self.PRETO
            )

            self.tela.blit(
                texto_valor,
                (rect.x + 7, rect.y + 5)
            )

            texto_unidade = self.fonte.render(
                unidade, True, self.PRETO
            )

            self.tela.blit(
                texto_unidade,
                (rect.right + 8, rect.y + 5)
            )

    def processar_evento_campo(self, evento, jogo):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.campo_ativo = None

            for nome, campo in self.campos.items():
                if campo["rect"].collidepoint(evento.pos):
                    self.campo_ativo = nome
                    break

        elif evento.type == pygame.KEYDOWN and self.campo_ativo:
            campo = self.campos[self.campo_ativo]

            if evento.key == pygame.K_RETURN:
                try:
                    valor = float(
                        campo["texto"].replace(",", ".")
                    )

                    if self.campo_ativo == "angulo":
                        if not 0 <= valor <= 90:
                            raise ValueError

                        if jogo.canhao is not None:
                            jogo.canhao.angulo = valor

                    elif self.campo_ativo == "velocidade":
                        if valor <= 0:
                            raise ValueError

                        if jogo.canhao is not None:
                            jogo.canhao.velocidade_inicial = valor

                    elif self.campo_ativo == "gravidade":
                        if valor <= 0:
                            raise ValueError

                        jogo.GRAVIDADE = valor

                    self.campo_ativo = None

                except ValueError:
                    # Valor inválido: mantém o campo
                    # ativo para que o jogador possa corrigi-lo.
                    pass

            elif evento.key == pygame.K_BACKSPACE:
                campo["texto"] = campo["texto"][:-1]

            elif evento.unicode and evento.unicode in "0123456789.,-":
                campo["texto"] += evento.unicode

    def mostrar_mensagem(self, mensagem):
        self.mensagem = mensagem
        self.tempo_mensagem = pygame.time.get_ticks() + 2000

    def desenhar_mensagem(self):
        if not hasattr(self, "mensagem") or not self.mensagem:
            return

        if pygame.time.get_ticks() > self.tempo_mensagem:
            self.mensagem = ""
            return

        fonte = pygame.font.SysFont("Arial", 30, bold=True)

        texto = fonte.render(
            self.mensagem,
            True,
            (255, 0, 0)
        )

        # Centraliza a mensagem na tela
        retangulo = texto.get_rect(
            center=(
                self.tela.get_width() // 2,
                self.tela.get_height() // 2
            )
        )

        self.tela.blit(texto, retangulo)

    def desenhar_interface(self, jogo):

        titulo = self.fonte_titulo.render(
            "ATINJA O ALVO",
            True,
            self.PRETO
        )

        self.tela.blit(
            titulo,
            (20, 20)
        )

    def desenhar_editor(self):

        # Fundo da caixa
        pygame.draw.rect(
            self.tela,
            self.BRANCO,
            self.editor_rect
        )

        # Borda da caixa
        cor_borda = (
            self.AZUL
            if self.editor_ativo
            else self.PRETO
        )

        pygame.draw.rect(
            self.tela,
            cor_borda,
            self.editor_rect,
            3
        )

        # Título do editor
        titulo = self.fonte_titulo.render(
            "PROGRAMA DO JOGADOR",
            True,
            self.PRETO
        )

        self.tela.blit(
            titulo,
            (self.editor_rect.x, self.editor_rect.y - 35)
        )

        # Desenha cada linha digitada
        y = self.editor_rect.y + 6

        for numero, linha in enumerate(self.linhas_codigo):
            # Número da linha
            numero_linha = self.fonte.render(
                f"{numero + 1}",
                True,
                self.CINZA
            )

            self.tela.blit(
                numero_linha,
                (
                    self.editor_rect.x + 10,
                    y
                )
            )

            # Código
            texto = self.fonte.render(
                linha,
                True,
                self.PRETO
            )

            self.tela.blit(
                texto,
                (
                    self.editor_rect.x + 45,
                    y
                )
            )

            y += 28

        # Cursor
        if self.editor_ativo:
            linha = self.linhas_codigo[
                self.linha_atual
            ]

            texto_antes_cursor = linha[
                :self.cursor_posicao
            ]

            largura_texto = self.fonte.size(
                texto_antes_cursor
            )[0]

            cursor_x = (
                    self.editor_rect.x
                    + 45
                    + largura_texto
            )

            cursor_y = (
                    self.editor_rect.y
                    + 10
                    + self.linha_atual * 28
            )

            pygame.draw.line(
                self.tela,
                self.PRETO,
                (
                    cursor_x,
                    cursor_y
                ),
                (
                    cursor_x,
                    cursor_y + 24
                ),
                2
            )

        # ======================================================
        # BOTÃO EXECUTAR
        # ======================================================

        pygame.draw.rect(
            self.tela,
            self.AZUL,
            self.botao_executar,
            border_radius=8
        )

        texto_botao = self.fonte.render(
            "EXECUTAR",
            True,
            self.BRANCO
        )

        texto_rect = texto_botao.get_rect(
            center=self.botao_executar.center
        )

        self.tela.blit(
            texto_botao,
            texto_rect
        )

        pygame.draw.rect(
            self.tela,
            self.VERMELHO,
            self.botao_reiniciar,
            border_radius=8
        )

        texto_botao = self.fonte.render(
            "REINICIAR",
            True,
            self.BRANCO
        )

        texto_rect = texto_botao.get_rect(
            center=self.botao_reiniciar.center
        )

        self.tela.blit(
            texto_botao,
            texto_rect
        )

    def processar_evento_editor(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if self.editor_rect.collidepoint(evento.pos):
                    self.editor_ativo = True

                    # Identifica a linha clicada
                    altura_linha = 28

                    y_relativo = (
                            evento.pos[1]
                            - self.editor_rect.y
                            - 6
                    )

                    linha_clicada = y_relativo // altura_linha

                    # Limita a seleção às linhas existentes
                    linha_clicada = max(
                        0,
                        min(
                            linha_clicada,
                            len(self.linhas_codigo) - 1
                        )
                    )

                    self.linha_atual = linha_clicada

                    # Identifica a coluna clicada
                    texto = self.linhas_codigo[self.linha_atual]

                    x_relativo = (
                            evento.pos[0]
                            - self.editor_rect.x
                            - 45
                    )

                    # Procura a posição do cursor mais próxima
                    # da posição horizontal do clique
                    self.cursor_posicao = 0
                    menor_distancia = abs(x_relativo)

                    for i in range(1, len(texto) + 1):

                        largura = self.fonte.size(texto[:i])[0]
                        distancia = abs(x_relativo - largura)

                        if distancia < menor_distancia:
                            menor_distancia = distancia
                            self.cursor_posicao = i

                    return "EDITOR"

                else:

                    self.editor_ativo = False

                if self.botao_executar.collidepoint(evento.pos):
                    return "EXECUTAR"

                if self.botao_reiniciar.collidepoint(evento.pos):
                    return "REINICIAR"

        if evento.type == pygame.KEYDOWN:

            if not self.editor_ativo:
                return None

            linha = self.linhas_codigo[self.linha_atual]

            if evento.key == pygame.K_RETURN:

                antes = linha[:self.cursor_posicao]
                depois = linha[self.cursor_posicao:]

                self.linhas_codigo[self.linha_atual] = antes

                self.linhas_codigo.insert(
                    self.linha_atual + 1,
                    depois
                )

                self.linha_atual += 1
                self.cursor_posicao = 0

            elif evento.key == pygame.K_BACKSPACE:

                if self.cursor_posicao > 0:

                    self.linhas_codigo[self.linha_atual] = (
                            linha[:self.cursor_posicao - 1]
                            + linha[self.cursor_posicao:]
                    )

                    self.cursor_posicao -= 1

                elif self.linha_atual > 0:

                    linha_anterior = self.linhas_codigo[
                        self.linha_atual - 1
                        ]

                    tamanho_anterior = len(linha_anterior)

                    self.linhas_codigo[self.linha_atual - 1] += linha

                    del self.linhas_codigo[self.linha_atual]

                    self.linha_atual -= 1
                    self.cursor_posicao = tamanho_anterior

            elif evento.key == pygame.K_DELETE:

                if self.cursor_posicao < len(linha):

                    self.linhas_codigo[self.linha_atual] = (
                            linha[:self.cursor_posicao]
                            + linha[self.cursor_posicao + 1:]
                    )

                elif self.linha_atual < len(self.linhas_codigo) - 1:

                    self.linhas_codigo[self.linha_atual] += (
                        self.linhas_codigo[self.linha_atual + 1]
                    )

                    del self.linhas_codigo[self.linha_atual + 1]

            elif evento.key == pygame.K_LEFT:

                if self.cursor_posicao > 0:
                    self.cursor_posicao -= 1

                elif self.linha_atual > 0:
                    self.linha_atual -= 1
                    self.cursor_posicao = len(
                        self.linhas_codigo[self.linha_atual]
                    )

            elif evento.key == pygame.K_RIGHT:

                if self.cursor_posicao < len(linha):
                    self.cursor_posicao += 1

                elif self.linha_atual < len(self.linhas_codigo) - 1:
                    self.linha_atual += 1
                    self.cursor_posicao = 0

            elif evento.key == pygame.K_UP:

                if self.linha_atual > 0:
                    self.linha_atual -= 1
                    self.cursor_posicao = min(
                        self.cursor_posicao,
                        len(self.linhas_codigo[self.linha_atual])
                    )

            elif evento.key == pygame.K_DOWN:

                if self.linha_atual < len(self.linhas_codigo) - 1:
                    self.linha_atual += 1
                    self.cursor_posicao = min(
                        self.cursor_posicao,
                        len(self.linhas_codigo[self.linha_atual])
                    )

            elif evento.unicode and evento.unicode.isprintable():

                self.linhas_codigo[self.linha_atual] = (
                        linha[:self.cursor_posicao]
                        + evento.unicode
                        + linha[self.cursor_posicao:]
                )
                self.cursor_posicao += len(evento.unicode)

        return None

    def obter_codigo(self):
        return "\n".join(
            self.linhas_codigo
        )

    def limpar_codigo(self):
        self.linhas_codigo = [""]
        self.linha_atual = 0
        self.cursor_posicao = 0
        self.editor_ativo = False

    def desenhar_alvo(self, alvo):

        if alvo is None:
            return

        x, y = self.mundo_para_tela(
            alvo.x,
            alvo.y
        )

        raio_pixels = int(
            alvo.raio * self.escala
        )

        raio_pixels = max(
            raio_pixels,
            8
        )

        pygame.draw.circle(
            self.tela,
            self.VERMELHO,
            (x, y),
            raio_pixels
        )

    def processar_evento_tela_inicial(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.botao_iniciar.collidepoint(evento.pos):
                return "INICIAR"
            if self.botao_tutorial.collidepoint(evento.pos):
                return "TUTORIAL"
        return None

    def desenhar_tela_inicial(self):
        self.tela.fill(self.BRANCO)

        fonte_titulo = pygame.font.SysFont(
            "Arial",
            48,
            bold=True
        )

        titulo = fonte_titulo.render(
            "ATINJA O ALVO",
            True,
            self.PRETO
        )

        titulo_rect = titulo.get_rect(
            center=(
                self.largura // 2,
                100
            )
        )

        self.tela.blit(
            titulo,
            titulo_rect
        )

        fonte_subtitulo = pygame.font.SysFont(
            "Arial",
            22
        )

        subtitulo = fonte_subtitulo.render(
            "Aprenda lançamento oblíquo programando!",
            True,
            self.PRETO
        )

        subtitulo_rect = subtitulo.get_rect(
            center=(
                self.largura // 2,
                160
            )
        )

        self.tela.blit(
            subtitulo,
            subtitulo_rect
        )

        fonte_instrucao = pygame.font.SysFont(
            "Arial",
            20
        )

        pygame.draw.rect(
            self.tela,
            self.VERDE,
            self.botao_iniciar,
            border_radius=10
        )

        self.desenhar_ilustracao_inicial()

        texto_botao = fonte_instrucao.render(
            "INICIAR JOGO",
            True,
            self.BRANCO
        )

        texto_rect = texto_botao.get_rect(
            center=self.botao_iniciar.center
        )

        self.tela.blit(
            texto_botao,
            texto_rect
        )

        # Botão COMO JOGAR
        pygame.draw.rect(
            self.tela,
            self.AZUL,
            self.botao_tutorial,
            border_radius=10
        )

        texto_tutorial = fonte_instrucao.render(
            "COMO JOGAR?",
            True,
            self.BRANCO
        )

        texto_rect = texto_tutorial.get_rect(
            center=self.botao_tutorial.center
        )

        self.tela.blit(
            texto_tutorial,
            texto_rect
        )

    def desenhar_tutorial(self):

        self.tela.fill(self.BRANCO)

        fonte_titulo = pygame.font.SysFont(
            "Arial", 36, bold=True
        )

        fonte_texto = pygame.font.SysFont(
            "Arial", 23
        )

        fonte_codigo = pygame.font.SysFont(
            "Consolas", 22
        )

        titulo = fonte_titulo.render(
            "COMO JOGAR?",
            True,
            self.PRETO
        )

        self.tela.blit(
            titulo,
            titulo.get_rect(
                center=(self.largura // 2, 65)
            )
        )

        instrucoes = [
            "Seu objetivo e programar o canhao para atingir o alvo.",
            "",
            "COMANDOS",
            "ANGULO: define o angulo de lancamento.",
            "VELOCIDADE: define a velocidade inicial.",
            "DISPARAR: realiza o lancamento do projetil.",
            "REPITA ATE ATINGIR: repete os comandos ate acertar.",
            "",
            "EXEMPLO DE PROGRAMA"
        ]

        y = 125

        for texto in instrucoes:
            superficie = fonte_texto.render(
                texto,
                True,
                self.PRETO
            )

            self.tela.blit(
                superficie,
                (100, y)
            )

            y += 38

        exemplo = [
            "repita ate atingir",
            "    disparar",
            "    velocidade++",
            "    angulo++",
            "fim"
        ]

        y += 5

        for linha in exemplo:
            superficie = fonte_codigo.render(
                linha,
                True,
                self.AZUL
            )

            self.tela.blit(
                superficie,
                (125, y)
            )

            y += 32

        texto_voltar = fonte_texto.render(
            "VOLTAR",
            True,
            self.BRANCO
        )

        pygame.draw.rect(
            self.tela,
            self.VERMELHO,
            self.botao_voltar_tutorial,
            border_radius=10
        )

        self.tela.blit(
            texto_voltar,
            texto_voltar.get_rect(
                center=self.botao_voltar_tutorial.center
            )
        )

        # Botão INICIAR JOGO
        pygame.draw.rect(
            self.tela,
            self.VERDE,
            self.botao_iniciar_tutorial,
            border_radius=10
        )

        texto_iniciar = fonte_texto.render(
            "INICIAR JOGO",
            True,
            self.BRANCO
        )

        self.tela.blit(
            texto_iniciar,
            texto_iniciar.get_rect(
                center=self.botao_iniciar_tutorial.center
            )
        )

    def processar_evento_tutorial(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:

                # Voltar para a tela inicial
                if self.botao_voltar_tutorial.collidepoint(evento.pos):
                    return "VOLTAR"

                # Iniciar o jogo diretamente pelo tutorial
                if self.botao_iniciar_tutorial.collidepoint(evento.pos):
                    return "INICIAR"

        return None

    def desenhar_ilustracao_inicial(self):

        # Posições calculadas proporcionalmente à tela
        w = self.largura
        h = self.altura

        chao_y = int(h * 0.72)

        canhao_x = int(w * 0.29)
        canhao_y = chao_y - 20

        alvo_x = int(w * 0.70)
        alvo_y = chao_y - 55

        # Cores
        azul_trajetoria = (50, 155, 230)
        vermelho = (230, 55, 55)
        vermelho_escuro = (170, 35, 35)
        verde = (80, 175, 85)
        verde_claro = (125, 210, 115)
        preto = (35, 35, 40)
        branco = (255, 255, 255)

        # --------------------------------------------------
        # CHÃO
        # --------------------------------------------------

        pygame.draw.line(
            self.tela,
            verde,
            (int(w * 0.20), chao_y),
            (int(w * 0.80), chao_y),
            5
        )

        # Pequenos detalhes de grama
        for x in [
            int(w * 0.24),
            int(w * 0.38),
            int(w * 0.62),
            int(w * 0.76)
        ]:
            pygame.draw.line(
                self.tela, verde_claro,
                (x, chao_y),
                (x - 6, chao_y - 12), 3
            )
            pygame.draw.line(
                self.tela, verde_claro,
                (x, chao_y),
                (x + 7, chao_y - 10), 3
            )

        # --------------------------------------------------
        # TRAJETÓRIA PARABÓLICA PONTILHADA
        # --------------------------------------------------

        inicio = (canhao_x + 20, canhao_y - 28)
        fim = (alvo_x - 12, alvo_y - 8)

        pontos = []

        for i in range(101):
            t = i / 100

            x = inicio[0] + (fim[0] - inicio[0]) * t

            y = (
                    inicio[1] * (1 - t)
                    + fim[1] * t
                    - 125 * 4 * t * (1 - t)
            )

            pontos.append((int(x), int(y)))

        # Desenha segmentos alternados para criar o pontilhado
        for i in range(0, len(pontos) - 1, 6):
            pygame.draw.line(
                self.tela,
                azul_trajetoria,
                pontos[i],
                pontos[min(i + 3, len(pontos) - 1)],
                4
            )

        # --------------------------------------------------
        # CANHÃO
        # --------------------------------------------------

        # Rodas
        pygame.draw.circle(
            self.tela, preto,
            (canhao_x, canhao_y), 25
        )

        pygame.draw.circle(
            self.tela, (185, 140, 80),
            (canhao_x, canhao_y), 15
        )

        pygame.draw.circle(
            self.tela, preto,
            (canhao_x, canhao_y), 5
        )

        # Cano inclinado
        pygame.draw.line(
            self.tela,
            preto,
            (canhao_x, canhao_y - 8),
            (canhao_x + 42, canhao_y - 39),
            22
        )

        pygame.draw.line(
            self.tela,
            (95, 100, 110),
            (canhao_x, canhao_y - 8),
            (canhao_x + 42, canhao_y - 39),
            15
        )

        # Boca do canhão
        pygame.draw.circle(
            self.tela,
            preto,
            (canhao_x + 42, canhao_y - 39),
            11
        )

        pygame.draw.circle(
            self.tela,
            (100, 105, 115),
            (canhao_x + 42, canhao_y - 39),
            6
        )

        # --------------------------------------------------
        # PROJÉTIL
        # --------------------------------------------------

        t = 0.43
        x = inicio[0] + (fim[0] - inicio[0]) * t
        y = (
                inicio[1] * (1 - t)
                + fim[1] * t
                - 125 * 4 * t * (1 - t)
        )

        pygame.draw.circle(
            self.tela,
            vermelho_escuro,
            (int(x), int(y)),
            12
        )

        pygame.draw.circle(
            self.tela,
            vermelho,
            (int(x), int(y)),
            9
        )

        # Brilho do projétil
        pygame.draw.circle(
            self.tela,
            (255, 150, 150),
            (int(x - 3), int(y - 3)),
            3
        )

        # --------------------------------------------------
        # ALVO
        # --------------------------------------------------

        pygame.draw.circle(
            self.tela,
            preto,
            (alvo_x, alvo_y),
            44
        )

        pygame.draw.circle(
            self.tela,
            vermelho,
            (alvo_x, alvo_y),
            39
        )

        pygame.draw.circle(
            self.tela,
            branco,
            (alvo_x, alvo_y),
            28
        )

        pygame.draw.circle(
            self.tela,
            vermelho,
            (alvo_x, alvo_y),
            17
        )

        pygame.draw.circle(
            self.tela,
            branco,
            (alvo_x, alvo_y),
            7
        )

        # Pés do alvo
        pygame.draw.line(
            self.tela, preto,
            (alvo_x - 20, alvo_y + 32),
            (alvo_x - 28, chao_y),
            7
        )

        pygame.draw.line(
            self.tela, preto,
            (alvo_x + 20, alvo_y + 32),
            (alvo_x + 28, chao_y),
            7
        )