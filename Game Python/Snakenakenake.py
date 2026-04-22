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
fuente = pygame.font.SysFont(None, 35)
fuente_fin = pygame.font.SysFont(None, 50)

OFFSET_CABEZA = int(TAM_BLOQUE * 0.15)

# =========================
# CARGA FIJA
# =========================
donut_img = pygame.image.load("img/Donut.png")
body_img = pygame.image.load("img/body.png")
tail_img = pygame.image.load("img/tail.png")

donut_img = pygame.transform.scale(donut_img, (TAM_BLOQUE, TAM_BLOQUE))
body_img = pygame.transform.scale(body_img, (TAM_BLOQUE, TAM_BLOQUE))
tail_img = pygame.transform.scale(tail_img, (TAM_BLOQUE, TAM_BLOQUE))


# =========================
# UTILIDAD
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
# SELECTOR CON CARRUSEL
# =========================
def seleccionar_personaje_paisaje():
    personajes = cargar_lista_imagenes(
        "img/heads",
        ["homer.png", "patty.png", "smithers.png", "marge.png", "bart.png", "lisa.png"],
        1.3
    )

    paisajes = [
        pygame.transform.scale(
            pygame.image.load(f"img/fons/{nombre}"),
            (ANCHO, ALTO)
        )
        for nombre in ["10.jpg","1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.png", "8.jpg", "9.jpg"]
    ]

    p_index = 0
    bg_index = 0

    while True:
        pantalla.fill(NEGRO)

        titulo = fuente.render("Selecciona personaje y paisaje", True, BLANCO)
        ayuda = fuente.render("A personaje | S paisaje | ENTER jugar", True, BLANCO)

        pantalla.blit(titulo, (120, 40))
        pantalla.blit(ayuda, (80, 80))

        # =========================
        # PERSONAJE (CARRUSEL)
        # =========================
        size_main = 80
        size_side = int(size_main * 0.3)

        prev_p = (p_index - 1) % len(personajes)
        next_p = (p_index + 1) % len(personajes)

        img_main = pygame.transform.scale(personajes[p_index], (size_main, size_main))
        img_prev = pygame.transform.scale(personajes[prev_p], (size_side, size_side))
        img_next = pygame.transform.scale(personajes[next_p], (size_side, size_side))

        img_prev.set_alpha(120)
        img_next.set_alpha(120)

        zona_personaje_x = ANCHO // 4
        zona_y = ALTO // 2 + 30

        x_main = zona_personaje_x - size_main // 2
        y_main = zona_y - size_main // 2

        x_prev = zona_personaje_x - size_main
        y_prev = zona_y - size_side // 2

        x_next = zona_personaje_x + size_main - size_side
        y_next = zona_y - size_side // 2

        pantalla.blit(img_prev, (x_prev, y_prev))
        pantalla.blit(img_main, (x_main, y_main))
        pantalla.blit(img_next, (x_next, y_next))

        pygame.draw.rect(pantalla, BLANCO, (x_main - 2, y_main - 2, size_main + 4, size_main + 4), 2)

        # =========================
        # FONDO (CARRUSEL + PERSPECTIVA)
        # =========================
        bg_main_w, bg_main_h = 200, 130
        bg_side_w = int(bg_main_w * 0.3)
        bg_side_h = int(bg_main_h * 0.3)

        prev_bg = (bg_index - 1) % len(paisajes)
        next_bg = (bg_index + 1) % len(paisajes)

        bg_main = pygame.transform.scale(paisajes[bg_index], (bg_main_w, bg_main_h))
        bg_prev = pygame.transform.scale(paisajes[prev_bg], (bg_side_w, bg_side_h))
        bg_next = pygame.transform.scale(paisajes[next_bg], (bg_side_w, bg_side_h))

        bg_prev.set_alpha(120)
        bg_next.set_alpha(120)

        zona_fondo_x = 3 * ANCHO // 4
        zona_y_bg = ALTO // 2 + 30

        separacion = 140

        x_main_bg = zona_fondo_x - bg_main_w // 2
        y_main_bg = zona_y_bg - bg_main_h // 2

        x_prev_bg = zona_fondo_x - separacion - bg_side_w // 2
        y_prev_bg = zona_y_bg - bg_side_h // 2

        x_next_bg = zona_fondo_x + separacion - bg_side_w // 2
        y_next_bg = zona_y_bg - bg_side_h // 2

        bg_prev_small = pygame.transform.scale(bg_prev, (int(bg_side_w * 0.9), int(bg_side_h * 0.9)))
        bg_next_small = pygame.transform.scale(bg_next, (int(bg_side_w * 0.9), int(bg_side_h * 0.9)))

        pantalla.blit(bg_prev_small, (x_prev_bg, y_prev_bg))
        pantalla.blit(bg_next_small, (x_next_bg, y_next_bg))
        pantalla.blit(bg_main, (x_main_bg, y_main_bg))

        pygame.draw.rect(
            pantalla,
            BLANCO,
            (x_main_bg - 2, y_main_bg - 2, bg_main_w + 4, bg_main_h + 4),
            2
        )

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_a:
                    p_index = (p_index + 1) % len(personajes)

                elif evento.key == pygame.K_s:
                    bg_index = (bg_index + 1) % len(paisajes)

                elif evento.key == pygame.K_RETURN:
                    return personajes[p_index], paisajes[bg_index]


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
def dibujar_snake(snake, head_img):
    for i, bloque in enumerate(snake):
        if len(snake) == 1:
            pantalla.blit(head_img, (bloque[0] - OFFSET_CABEZA, bloque[1] - OFFSET_CABEZA))
        elif i == 0:
            pantalla.blit(tail_img, (bloque[0], bloque[1]))
        elif i == len(snake) - 1:
            pantalla.blit(head_img, (bloque[0] - OFFSET_CABEZA, bloque[1] - OFFSET_CABEZA))
        else:
            pantalla.blit(body_img, (bloque[0], bloque[1]))


# =========================
# UI
# =========================
def mostrar_puntuacion(puntos):
    texto = fuente.render(f"Puntos: {puntos}", True, BLANCO)
    pantalla.blit(texto, (10, 10))


def pantalla_game_over(fondo):
    while True:
        pantalla.blit(fondo, (0, 0))

        # =========================
        # OVERLAY OSCURECIDO (DIFUMINADO VISUAL)
        # =========================
        overlay = pygame.Surface((ANCHO, ALTO))
        # =========================================
        # CONTROL DE INTENSIDAD DEL EFECTO
        overlay.set_alpha(110)
        # =========================================
        overlay.fill((0, 0, 0))
        pantalla.blit(overlay, (0, 0))

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
        head_img, fondo_img = seleccionar_personaje_paisaje()

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

            # =========================
            # OVERLAY OSCURECIDO (JUEGO)
            # =========================
            overlay = pygame.Surface((ANCHO, ALTO))
            # =========================================
            # CONTROL DE INTENSIDAD DEL EFECTO
            overlay.set_alpha(90)
            # =========================================
            overlay.fill((0, 0, 0))
            pantalla.blit(overlay, (0, 0))

            pantalla.blit(donut_img, (comida[0], comida[1]))

            dibujar_snake(snake, head_img)
            mostrar_puntuacion(puntos)

            pygame.display.update()
            reloj.tick(FPS)

        if not pantalla_game_over(fondo_img):
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    juego()