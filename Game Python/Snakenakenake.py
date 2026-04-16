import pygame
import sys
import random

pygame.init()

# Configuración
ANCHO = 600
ALTO = 400
TAM_BLOQUE = 20

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Snake")

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

reloj = pygame.time.Clock()
FPS = 10
fuente = pygame.font.SysFont(None, 35)
fuente_fin = pygame.font.SysFont(None, 50)

# =========================
# CARGAR IMÁGENES
# =========================
fondo_img = pygame.image.load("img/Springfield.png")
donut_img = pygame.image.load("img/Donut.png")
head_img = pygame.image.load("img/head.png")
body_img = pygame.image.load("img/body.png")
tail_img = pygame.image.load("img/tail.png")

# Escalar imágenes
fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
donut_img = pygame.transform.scale(donut_img, (TAM_BLOQUE, TAM_BLOQUE))
head_img = pygame.transform.scale(head_img, (TAM_BLOQUE, TAM_BLOQUE))
body_img = pygame.transform.scale(body_img, (TAM_BLOQUE, TAM_BLOQUE))
tail_img = pygame.transform.scale(tail_img, (TAM_BLOQUE, TAM_BLOQUE))


def crear_comida():
    x = random.randrange(0, ANCHO, TAM_BLOQUE)
    y = random.randrange(0, ALTO, TAM_BLOQUE)
    return [x, y]


def dibujar_snake(snake):
    for i, bloque in enumerate(snake):
        if len(snake) == 1:
            pantalla.blit(head_img, (bloque[0], bloque[1]))
        elif i == 0:
            pantalla.blit(tail_img, (bloque[0], bloque[1]))
        elif i == len(snake) - 1:
            pantalla.blit(head_img, (bloque[0], bloque[1]))
        else:
            pantalla.blit(body_img, (bloque[0], bloque[1]))


def mostrar_puntuacion(puntos):
    texto = fuente.render(f"Puntos: {puntos}", True, BLANCO)
    pantalla.blit(texto, (10, 10))


def pantalla_game_over():
    while True:
        pantalla.blit(fondo_img, (0, 0))

        texto1 = fuente_fin.render("GAME OVER", True, ROJO)
        texto2 = fuente.render("Pulsa R para reiniciar", True, BLANCO)
        texto3 = fuente.render("Pulsa ESC para salir", True, BLANCO)

        pantalla.blit(texto1, (ANCHO // 2 - 120, ALTO // 2 - 60))
        pantalla.blit(texto2, (ANCHO // 2 - 140, ALTO // 2))
        pantalla.blit(texto3, (ANCHO // 2 - 120, ALTO // 2 + 40))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def juego():
    while True:
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

            # DIBUJAR FONDO
            pantalla.blit(fondo_img, (0, 0))

            # Dibujar donut
            pantalla.blit(donut_img, (comida[0], comida[1]))

            # Dibujar serpiente
            dibujar_snake(snake)

            mostrar_puntuacion(puntos)

            pygame.display.update()
            reloj.tick(FPS)

        pantalla_game_over()


if __name__ == "__main__":
    juego()