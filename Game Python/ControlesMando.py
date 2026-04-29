import pygame

class Mando:

    def __init__(self):

        pygame.joystick.init()

        self.joystick = None
        self.deadzone = 0.3

    # =========================
    # INIT SAFE
    # =========================
    def update(self):

        if self.joystick is None:

            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()

    # =========================
    # BOTONES
    # =========================
    def A(self):
        if self.joystick:
            return self.joystick.get_button(0)
        return False

    def B(self):
        if self.joystick:
            return self.joystick.get_button(1)
        return False

    def START(self):
        if self.joystick:
            return self.joystick.get_button(7)
        return False

    # =========================
    # MOVIMIENTO JUEGO
    # =========================
    def direccion_juego(self):

        if not self.joystick:
            return None

        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)

        if abs(x) < self.deadzone and abs(y) < self.deadzone:
            return None

        if abs(x) > abs(y):
            return "LEFT" if x < 0 else "RIGHT"
        else:
            return "UP" if y < 0 else "DOWN"

    # =========================
    # SELECTOR PERSONAJE
    # =========================
    def selector_personaje(self):

        if not self.joystick:
            return None

        x = self.joystick.get_axis(0)

        if abs(x) < self.deadzone:
            return None

        return "LEFT" if x < 0 else "RIGHT"

    # =========================
    # SELECTOR FONDO
    # =========================
    def selector_fondo(self):

        if not self.joystick:
            return None

        x = self.joystick.get_axis(2)

        if abs(x) < self.deadzone:
            return None

        return "LEFT" if x < 0 else "RIGHT"