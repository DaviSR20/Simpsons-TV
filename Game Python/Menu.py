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

    # =========================
    # PAUSA PRINCIPAL
    # =========================
    def run(self):

        while True:

            self.handle_input()
            self.draw()

            accion = self.get_action()
            if accion:
                return accion

            pygame.time.delay(16)

    # =========================
    # INPUT
    # =========================
    def handle_input(self):

        keys = pygame.key.get_pressed()

        if self.cooldown > 0:
            self.cooldown -= 1
            return

        # =========================
        # TECLADO
        # =========================
        if keys[pygame.K_UP]:
            self.opcion = (self.opcion - 1) % len(self.opciones)
            self.cooldown = 10

        if keys[pygame.K_DOWN]:
            self.opcion = (self.opcion + 1) % len(self.opciones)
            self.cooldown = 10

        if keys[pygame.K_RETURN]:
            self.confirm()

        if keys[pygame.K_ESCAPE]:
            self.opcion = 0
            return "CONTINUAR"

        # =========================
        # MANDO
        # =========================
        self.mando.update()

        diry = self.mando.direccion_juego()

        if diry == "UP":
            self.opcion = (self.opcion - 1) % len(self.opciones)
            self.cooldown = 10

        if diry == "DOWN":
            self.opcion = (self.opcion + 1) % len(self.opciones)
            self.cooldown = 10

        if self.mando.A():
            self.confirm()

        if self.mando.B():
            return "SALIR"

    # =========================
    # CONFIRMAR OPCIÓN
    # =========================
    def confirm(self):

        selected = self.opciones[self.opcion]

        if selected == "CONTINUAR":
            self.result = "CONTINUAR"

        elif selected == "REINICIAR":
            self.result = "REINICIAR"

        elif selected == "SALIR":
            self.result = "SALIR"

    def get_action(self):

        if hasattr(self, "result"):
            return self.result
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
            "↑↓ o joystick = mover | ENTER/A = seleccionar | B = salir | ESC = continuar",
            True,
            (150, 150, 150)
        )

        self.pantalla.blit(info, (self.ancho//2 - info.get_width()//2, self.alto - 60))

        pygame.display.update()