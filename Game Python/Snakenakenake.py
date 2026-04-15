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
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
BLANCO = (255, 255, 255)

reloj = pygame.time.Clock()
FPS = 10
fuente = pygame.font.SysFont(None, 35)
fuente_fin = pygame.font.SysFont(None, 50)


def crear_comida():
    x = random.randrange(0, ANCHO, TAM_BLOQUE)
    y = random.randrange(0, ALTO, TAM_BLOQUE)
    return [x, y]


def dibujar_snake(snake):
    for bloque in snake:
        pygame.draw.rect(
            pantalla,
            VERDE,
            (bloque[0], bloque[1], TAM_BLOQUE, TAM_BLOQUE)
        )


def mostrar_puntuacion(puntos):
    texto = fuente.render(f"Puntos: {puntos}", True, VERDE)
    pantalla.blit(texto, (10, 10))


def pantalla_game_over():
    while True:
        pantalla.fill(NEGRO)

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
                    return  # vuelve a empezar el juego
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def juego():
    while True:  # bucle para reiniciar
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

            # Movimiento
            x += dx
            y += dy

            # Aparecer por el lado contrario
            x = x % ANCHO
            y = y % ALTO

            cabeza = [x, y]
            snake.append(cabeza)

            if len(snake) > longitud:
                del snake[0]

            # Colisión consigo misma
            if cabeza in snake[:-1]:
                jugando = False

            # Comer comida
            if cabeza == comida:
                comida = crear_comida()
                longitud += 1
                puntos += 1

            pantalla.fill(NEGRO)

            pygame.draw.rect(
                pantalla,
                ROJO,
                (comida[0], comida[1], TAM_BLOQUE, TAM_BLOQUE)
            )

            dibujar_snake(snake)
            mostrar_puntuacion(puntos)

            pygame.display.update()
            reloj.tick(FPS)

        pantalla_game_over()


if __name__ == "__main__":
    juego()