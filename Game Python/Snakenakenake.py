import pygame
import sys
import random

pygame.init()

from Selector import selector
from ControlesMando import Mando

mando = Mando()

# =========================
# CONFIG
# =========================
ANCHO = 600
ALTO = 400
TAM_BLOQUE = 20
HEAD_SIZE = int(TAM_BLOQUE * 1.5)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Snake")

reloj = pygame.time.Clock()
FPS = 7

NEGRO = (0,0,0)
BLANCO = (255,255,255)
ROJO = (255,0,0)

fuente = pygame.font.SysFont(None, 30)
fuente_fin = pygame.font.SysFont(None, 50)

# =========================
# PERSONAJES
# =========================
personajes = [
    pygame.image.load("img/heads/homer.png"),
    pygame.image.load("img/heads/patty.png"),
    pygame.image.load("img/heads/smithers.png"),
    pygame.image.load("img/heads/marge.png"),
    pygame.image.load("img/heads/bart.png"),
    pygame.image.load("img/heads/lisa.png")
]

# =========================
# FONDOS
# =========================
fondos = [
    pygame.image.load(f"img/fons/{n}")
    for n in ["10.jpg","1.jpg","2.jpg","3.jpg","4.jpg","5.jpg","6.jpg","7.png","9.jpg","8.jpg"]
]

# =========================
# IMÁGENES SNAKE
# =========================
donut_img = pygame.transform.smoothscale(
    pygame.image.load("img/Donut.png"),
    (TAM_BLOQUE, TAM_BLOQUE)
)

body_img = pygame.transform.smoothscale(
    pygame.image.load("img/body.png"),
    (TAM_BLOQUE, TAM_BLOQUE)
)

tail_img = pygame.transform.smoothscale(
    pygame.image.load("img/tail.png"),
    (TAM_BLOQUE, TAM_BLOQUE)
)

# =========================
# COMIDA
# =========================
def crear_comida(snake):
    while True:
        pos = [
            random.randrange(0, ANCHO, TAM_BLOQUE),
            random.randrange(0, ALTO, TAM_BLOQUE)
        ]
        if pos not in snake:
            return pos

# =========================
# GAME OVER
# =========================
def game_over():

    pygame.event.clear()
    mando.update()

    while True:

        mando.update()

        pantalla.fill(NEGRO)
        pantalla.blit(fuente_fin.render("GAME OVER", True, ROJO), (160,150))
        pantalla.blit(fuente.render("A reiniciar | B salir", True, BLANCO), (150,220))

        pygame.display.update()

        if mando.A():
            pygame.event.clear()
            return "RESTART"

        if mando.B():
            pygame.quit()
            sys.exit()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# =========================
# PAUSA
# =========================
def pausa():

    pygame.event.clear()
    mando.update()

    while True:

        mando.update()

        pantalla.fill(NEGRO)
        pantalla.blit(fuente_fin.render("PAUSA", True, BLANCO), (230,150))
        pantalla.blit(fuente.render("A continuar | B salir", True, BLANCO), (160,220))

        pygame.display.update()

        if mando.A():
            pygame.event.clear()
            return "CONTINUE"

        if mando.B():
            pygame.quit()
            sys.exit()

# =========================
# JUEGO
# =========================
def juego():

    while True:

        pygame.event.clear()

        # 🔥 SELECTOR CORRECTO
        head_img, fondo_img = selector(
            pantalla,
            reloj,
            mando,
            personajes,
            fondos
        )

        head_img = pygame.transform.smoothscale(head_img, (HEAD_SIZE, HEAD_SIZE))

        x = ANCHO // 2
        y = ALTO // 2

        dx = TAM_BLOQUE
        dy = 0

        snake = [[x,y]]
        longitud = 1

        comida = crear_comida(snake)

        jugando = True

        while jugando:

            mando.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        res = pausa()
                        if res == "EXIT":
                            pygame.quit()
                            sys.exit()

            # MOVIMIENTO MANDO
            dirj = mando.direccion_juego()

            if dirj == "UP" and dy == 0:
                dx, dy = 0, -TAM_BLOQUE
            elif dirj == "DOWN" and dy == 0:
                dx, dy = 0, TAM_BLOQUE
            elif dirj == "LEFT" and dx == 0:
                dx, dy = -TAM_BLOQUE, 0
            elif dirj == "RIGHT" and dx == 0:
                dx, dy = TAM_BLOQUE, 0

            x = (x + dx) % ANCHO
            y = (y + dy) % ALTO

            cabeza = [x,y]
            snake.append(cabeza)

            if len(snake) > longitud:
                snake.pop(0)

            # COLISIÓN
            if cabeza in snake[:-1]:
                r = game_over()

                if r == "RESTART":
                    jugando = False
                    break

            # COMIDA
            if cabeza == comida:
                comida = crear_comida(snake)
                longitud += 1

            # RENDER FONDO
            fondo_render = pygame.transform.smoothscale(fondo_img, (ANCHO, ALTO))
            pantalla.blit(fondo_render, (0,0))

            pantalla.blit(donut_img, comida)

            offset = (TAM_BLOQUE - HEAD_SIZE) // 2

            for i,b in enumerate(snake):

                if i == len(snake)-1:
                    pantalla.blit(head_img, (b[0] + offset, b[1] + offset))
                elif i == 0:
                    pantalla.blit(tail_img, b)
                else:
                    pantalla.blit(body_img, b)

            pygame.display.update()
            reloj.tick(FPS)

# =========================
# START
# =========================
if __name__ == "__main__":
    juego()