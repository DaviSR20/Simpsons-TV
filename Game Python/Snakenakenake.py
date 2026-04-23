import pygame
import sys
import random

pygame.init()

# =========================
# CONFIGURACIÓN
# =========================
ANCHO = 600
ALTO = 400
TAM_BLOQUE = 20

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Snake")

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

reloj = pygame.time.Clock()
FPS = 7

fuente = pygame.font.SysFont(None, 30)
fuente_fin = pygame.font.SysFont(None, 50)

# =========================
# IMÁGENES FIJAS
# =========================
donut_img = pygame.transform.scale(
    pygame.image.load("img/Donut.png"), (TAM_BLOQUE, TAM_BLOQUE)
)
body_img = pygame.transform.scale(
    pygame.image.load("img/body.png"), (TAM_BLOQUE, TAM_BLOQUE)
)
tail_img = pygame.transform.scale(
    pygame.image.load("img/tail.png"), (TAM_BLOQUE, TAM_BLOQUE)
)

# =========================
# UTILIDAD IMÁGENES
# =========================
def cargar_lista_imagenes(ruta, nombres, escala=1.0):
    size = int(TAM_BLOQUE * escala)
    return [
        pygame.transform.scale(
            pygame.image.load(f"{ruta}/{n}"), (size, size)
        )
        for n in nombres
    ]

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
# SELECTOR (RESTAURADO)
# =========================
def selector():

    personajes = cargar_lista_imagenes(
        "img/heads",
        ["homer.png","patty.png","smithers.png","marge.png","bart.png","lisa.png"],
        1.2
    )

    fondos = [
        pygame.transform.scale(
            pygame.image.load(f"img/fons/{n}"),
            (ANCHO, ALTO)
        )
        for n in ["10.jpg","1.jpg","2.jpg","3.jpg","4.jpg","5.jpg","6.jpg","7.png","9.jpg","8.jpg"]
    ]

    p_i = 0
    f_i = 0

    while True:

        pantalla.fill((30, 30, 30))

        pantalla.blit(fuente.render("Selecciona personaje y paisaje", True, BLANCO), (120, 20))
        pantalla.blit(fuente.render("← → personaje | A D fondo | ENTER jugar", True, BLANCO), (90, 60))

        # =========================
        # PERSONAJE
        # =========================
        cx = ANCHO // 4
        cy = ALTO // 2

        main = pygame.transform.scale(personajes[p_i], (80, 80))
        prev = pygame.transform.scale(personajes[(p_i - 1) % len(personajes)], (50, 50))
        nxt = pygame.transform.scale(personajes[(p_i + 1) % len(personajes)], (50, 50))

        prev.set_alpha(120)
        nxt.set_alpha(120)

        pantalla.blit(prev, prev.get_rect(center=(cx - 90, cy)))
        pantalla.blit(main, main.get_rect(center=(cx, cy)))
        pantalla.blit(nxt, nxt.get_rect(center=(cx + 90, cy)))

        # =========================
        # FONDO
        # =========================
        fx = 3 * ANCHO // 4
        fy = ALTO // 2

        bg_main = pygame.transform.scale(fondos[f_i], (160, 100))
        bg_prev = pygame.transform.scale(fondos[(f_i - 1) % len(fondos)], (110, 70))
        bg_next = pygame.transform.scale(fondos[(f_i + 1) % len(fondos)], (110, 70))

        bg_prev.set_alpha(120)
        bg_next.set_alpha(120)

        pantalla.blit(bg_prev, bg_prev.get_rect(center=(fx - 110, fy)))
        pantalla.blit(bg_main, bg_main.get_rect(center=(fx, fy)))
        pantalla.blit(bg_next, bg_next.get_rect(center=(fx + 110, fy)))

        pygame.display.update()
        reloj.tick(20)

        # =========================
        # INPUT SELECTOR
        # =========================
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_LEFT:
                    p_i = (p_i - 1) % len(personajes)

                if e.key == pygame.K_RIGHT:
                    p_i = (p_i + 1) % len(personajes)

                if e.key == pygame.K_a:
                    f_i = (f_i - 1) % len(fondos)

                if e.key == pygame.K_d:
                    f_i = (f_i + 1) % len(fondos)

                if e.key == pygame.K_RETURN:
                    return personajes[p_i], fondos[f_i]

# =========================
# PAUSA
# =========================
def pausa():

    while True:

        pantalla.fill((0, 0, 0))

        pantalla.blit(fuente_fin.render("PAUSA", True, BLANCO), (230, 150))
        pantalla.blit(fuente.render("ESC = volver | R = salir", True, BLANCO), (150, 220))

        pygame.display.update()

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_ESCAPE:
                    return True
                if e.key == pygame.K_r:
                    return False

# =========================
# GAME OVER
# =========================
def game_over():

    while True:

        pantalla.fill((0, 0, 0))

        pantalla.blit(fuente_fin.render("GAME OVER", True, ROJO), (160, 150))
        pantalla.blit(fuente.render("R = reiniciar | ESC = salir", True, BLANCO), (120, 220))

        pygame.display.update()

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_ESCAPE:
                    return False

# =========================
# JUEGO
# =========================
def juego():

    while True:

        head_img, fondo_img = selector()

        x = ANCHO // 2
        y = ALTO // 2

        dx = TAM_BLOQUE
        dy = 0

        snake = [[x, y]]
        longitud = 1

        comida = crear_comida(snake)

        jugando = True

        while jugando:

            for e in pygame.event.get():

                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_ESCAPE:
                        if not pausa():
                            return

                    if e.key == pygame.K_UP and dy == 0:
                        dx, dy = 0, -TAM_BLOQUE
                    elif e.key == pygame.K_DOWN and dy == 0:
                        dx, dy = 0, TAM_BLOQUE
                    elif e.key == pygame.K_LEFT and dx == 0:
                        dx, dy = -TAM_BLOQUE, 0
                    elif e.key == pygame.K_RIGHT and dx == 0:
                        dx, dy = TAM_BLOQUE, 0

            # =========================
            # MOVIMIENTO
            # =========================
            x = (x + dx) % ANCHO
            y = (y + dy) % ALTO

            cabeza = [x, y]
            snake.append(cabeza)

            if len(snake) > longitud:
                snake.pop(0)

            # =========================
            # COLISIÓN CON UNO MISMO
            # =========================
            if cabeza in snake[:-1]:
                if not game_over():
                    return

            # =========================
            # COMIDA
            # =========================
            if cabeza == comida:
                comida = crear_comida(snake)
                longitud += 1

            # =========================
            # RENDER
            # =========================
            pantalla.blit(fondo_img, (0, 0))
            pantalla.blit(donut_img, comida)

            for i, b in enumerate(snake):
                if i == len(snake) - 1:
                    pantalla.blit(head_img, b)
                elif i == 0:
                    pantalla.blit(tail_img, b)
                else:
                    pantalla.blit(body_img, b)

            pygame.display.update()
            reloj.tick(FPS)

# =========================
# INICIO
# =========================
if __name__ == "__main__":
    juego()