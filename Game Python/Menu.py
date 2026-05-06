import pygame
import sys

class Menu:

    def __init__(self, pantalla, mando):

        self.pantalla = pantalla
        self.mando = mando

        self.ancho, self.alto = pantalla.get_size()

        self.fuente = pygame.font.SysFont(None, 40)
        self.fuente_small = pygame.font.SysFont(None, 24)

        self.opciones = ["CONTINUAR", "REINICIAR", "SALIR"]
        self.opcion = 0

        self.cooldown = 0
        self.input_lock = 15  # evita input accidental al abrir

    # =========================
    # LOOP PRINCIPAL
    # =========================
    def run(self):

        pygame.event.clear()
        self.mando.update()

        while True:

            accion = self.handle_input()
            if accion:
                pygame.event.clear()
                return accion

            self.draw()
            pygame.time.delay(16)

    # =========================
    # INPUT
    # =========================
    def handle_input(self):

        self.mando.update()
        keys = pygame.key.get_pressed()

        # =========================
        # INPUT LOCK
        # =========================
        if self.input_lock > 0:
            self.input_lock -= 1
            return None

        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        # =========================
        # EVENTOS
        # =========================
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # =========================
        # TECLADO
        # =========================
        if keys[pygame.K_UP]:
            self.opcion = (self.opcion - 1) % len(self.opciones)
            self.cooldown = 10

        elif keys[pygame.K_DOWN]:
            self.opcion = (self.opcion + 1) % len(self.opciones)
            self.cooldown = 10

        elif keys[pygame.K_RETURN]:
            return self.opciones[self.opcion]

        elif keys[pygame.K_ESCAPE]:
            return "CONTINUAR"

        # =========================
        # MANDO
        # =========================
        diry = self.mando.direccion_juego()

        if diry == "UP":
            self.opcion = (self.opcion - 1) % len(self.opciones)
            self.cooldown = 10

        elif diry == "DOWN":
            self.opcion = (self.opcion + 1) % len(self.opciones)
            self.cooldown = 10

        # =========================
        # BOTONES
        # =========================
        if self.mando.A():
            return self.opciones[self.opcion]

        if self.mando.B():
            return "SALIR"

        # 🔥 START = CONTINUAR (como ESC)
        if self.mando.START():
            return "CONTINUAR"

        return None

    # =========================
    # RENDER
    # =========================
    def draw(self):

        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))

        title = self.fuente.render("PAUSA", True, (255, 255, 255))
        self.pantalla.blit(title, (self.ancho//2 - title.get_width()//2, 60))

        for i, opt in enumerate(self.opciones):

            color = (255, 255, 0) if i == self.opcion else (200, 200, 200)

            text = self.fuente.render(opt, True, color)

            self.pantalla.blit(
                text,
                (self.ancho//2 - text.get_width()//2, 160 + i * 50)
            )

        info = self.fuente_small.render(
            "↑↓ / joystick = mover | ENTER/A = seleccionar | START/ESC = continuar | B = salir",
            True,
            (150, 150, 150)
        )

        self.pantalla.blit(info, (self.ancho//2 - info.get_width()//2, self.alto - 60))

        pygame.display.update()