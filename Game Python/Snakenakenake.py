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
FPS = 7  # ↓ VELOCIDAD BAJADA
fuente = pygame.font.SysFont(None, 35)
fuente_fin = pygame.font.SysFont(None, 50)

# =========================
# FONDO Y COMIDA
# =========================
fondo_img = pygame.image.load("img/Springfield.png")
donut_img = pygame.image.load("img/Donut.png")

fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
donut_img = pygame.transform.scale(donut_img, (TAM_BLOQUE, TAM_BLOQUE))


# =========================
# CARGA DE IMÁGENES
# =========================
def cargar_lista_imagenes(ruta_base, nombres, escala=1.0):
    tamaño = int(TAM_BLOQUE * escala)

    return [
        pygame.transform.scale(
            pygame.image.load(f"{ruta_base}/{nombre}"),
            (tamaño, tamaño)
        )
        for nombre in nombres
    ]


# =========================
# SELECCIÓN DE SKIN
# =========================
def seleccionar_skin():
    heads = cargar_lista_imagenes(
        "img/heads",
        ["head.png", "head2.png", "head.jpg"],
        1.3  # ← CABEZA 30% MÁS GRANDE
    )

    bodies = cargar_lista_imagenes(
        "img/bodies",
        ["body.png", "body2.png", "body.jpg"]
    )

    tails = cargar_lista_imagenes(
        "img/tails",
        ["tail.png", "tail2.png", "tail.jpg"]
    )

    head_index = 0
    body_index = 0
    tail_index = 0

    while True:
        pantalla.fill(NEGRO)

        titulo = fuente.render("Selecciona tu serpiente", True, BLANCO)
        ayuda = fuente.render("A cabeza | S cuerpo | D cola | ENTER jugar", True, BLANCO)

        pantalla.blit(titulo, (150, 50))
        pantalla.blit(ayuda, (60, 100))

        pantalla.blit(heads[head_index], (100, 200))
        pantalla.blit(bodies[body_index], (270, 200))
        pantalla.blit(tails[tail_index], (440, 200))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_a:
                    head_index = (head_index + 1) % len(heads)

                elif evento.key == pygame.K_s:
                    body_index = (body_index + 1) % len(bodies)

                elif evento.key == pygame.K_d:
                    tail_index = (tail_index + 1) % len(tails)

                elif evento.key == pygame.K_RETURN:
                    return heads[head_index], bodies[body_index], tails[tail_index]


# =========================
# COMIDA
# =========================
def crear_comida():
    x = random.randrange(0, ANCHO, TAM_BLOQUE)
    y = random.randrange(0, ALTO, TAM_BLOQUE)
    return [x, y]


# =========================
# DIBUJAR SERPIENTE
# =========================
def dibujar_snake(snake, head_img, body_img, tail_img):
    for i, bloque in enumerate(snake):

        if len(snake) == 1:
            pantalla.blit(head_img, (bloque[0], bloque[1]))

        elif i == 0:
            pantalla.blit(tail_img, (bloque[0], bloque[1]))

        elif i == len(snake) - 1:
            # CABEZA 30% MÁS GRANDE PERO HITBOX IGUAL
            offset = int(TAM_BLOQUE * 0.15)
            pantalla.blit(head_img, (bloque[0] - offset, bloque[1] - offset))

        else:
            pantalla.blit(body_img, (bloque[0], bloque[1]))


# =========================
# PUNTUACIÓN
# =========================
def mostrar_puntuacion(puntos):
    texto = fuente.render(f"Puntos: {puntos}", True, BLANCO)
    pantalla.blit(texto, (10, 10))


# =========================
# GAME OVER
# =========================
def pantalla_game_over():
    while True:
        pantalla.blit(fondo_img, (0, 0))

        t1 = fuente_fin.render("GAME OVER", True, ROJO)
        t2 = fuente.render("R = reiniciar", True, BLANCO)
        t3 = fuente.render("ESC = salir", True, BLANCO)

        pantalla.blit(t1, (180, 150))
        pantalla.blit(t2, (200, 220))
        pantalla.blit(t3, (200, 260))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return True
                if evento.key == pygame.K_ESCAPE:
                    return False


# =========================
# JUEGO
# =========================
def juego():
    while True:

        head_img, body_img, tail_img = seleccionar_skin()

        x = ANCHO // 2
        y = ALTO // 2

        dx = TAM_BLOQUE
        dy = 0

        snake = [[x, y]]
        longitud = 1

        comida = crear_comida()
        puntos = 0

        jugando = True

        while jugando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP and dy == 0:
                        dx = 0
                        dy = -TAM_BLOQUE
                    elif evento.key == pygame.K_DOWN and dy == 0:
                        dx = 0
                        dy = TAM_BLOQUE
                    elif evento.key == pygame.K_LEFT and dx == 0:
                        dx = -TAM_BLOQUE
                        dy = 0
                    elif evento.key == pygame.K_RIGHT and dx == 0:
                        dx = TAM_BLOQUE
                        dy = 0

            x += dx
            y += dy

            x = x % ANCHO
            y = y % ALTO

            cabeza = [x, y]
            snake.append(cabeza)

            if len(snake) > longitud:
                del snake[0]

            if cabeza in snake[:-1]:
                jugando = False

            if cabeza == comida:
                comida = crear_comida()
                longitud += 1
                puntos += 1

            pantalla.blit(fondo_img, (0, 0))
            pantalla.blit(donut_img, (comida[0], comida[1]))

            dibujar_snake(snake, head_img, body_img, tail_img)
            mostrar_puntuacion(puntos)

            pygame.display.update()
            reloj.tick(FPS)

        if not pantalla_game_over():
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    juego()