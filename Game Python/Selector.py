import pygame
import sys

def selector(pantalla, reloj, mando, personajes, fondos):

    pygame.event.clear()
    mando.update()

    ANCHO, ALTO = pantalla.get_size()

    fuente_small = pygame.font.SysFont(None, 22)

    p_i = 0
    f_i = 0
    cooldown = 0

    input_lock = 20  # evita auto-input al entrar

    while True:

        mando.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # =========================
        # INPUT LOCK
        # =========================
        if input_lock > 0:
            input_lock -= 1
            pygame.display.update()
            reloj.tick(60)
            continue

        if cooldown > 0:
            cooldown -= 1

        move_p = mando.selector_personaje()
        move_f = mando.selector_fondo()

        # =========================
        # INPUT CARRUSEL
        # =========================
        if cooldown == 0:

            if keys[pygame.K_LEFT] or move_p == "LEFT":
                p_i = (p_i - 1) % len(personajes)
                cooldown = 8

            elif keys[pygame.K_RIGHT] or move_p == "RIGHT":
                p_i = (p_i + 1) % len(personajes)
                cooldown = 8

            if keys[pygame.K_a] or move_f == "LEFT":
                f_i = (f_i - 1) % len(fondos)
                cooldown = 8

            elif keys[pygame.K_d] or move_f == "RIGHT":
                f_i = (f_i + 1) % len(fondos)
                cooldown = 8

        # =========================
        # CONFIRMAR
        # =========================
        if keys[pygame.K_RETURN] or mando.A():
            pygame.event.clear()
            return personajes[p_i], fondos[f_i]

        if mando.B():
            pygame.quit()
            sys.exit()

        # =========================
        # RENDER
        # =========================
        pantalla.fill((20, 20, 20))

        legend = [
            "Selecciona personaje y paisaje",
            "A / Stick Izq = personaje | S / Stick Der = fondo",
            "ENTER / A = jugar"
        ]

        for i, line in enumerate(legend):
            txt = fuente_small.render(line, True, (220, 220, 220))
            pantalla.blit(txt, (ANCHO//2 - txt.get_width()//2, 30 + i * 22))

        # =========================
        # CENTRO GLOBAL
        # =========================
        centro_y = ALTO // 2 + 20

        # =========================
        # PERSONAJES (CARRUSEL)
        # =========================
        centro_x_p = ANCHO // 4
        offset_p = 80

        main_size = 90
        side_size = 60

        main = pygame.transform.smoothscale(personajes[p_i], (main_size, main_size))
        prev = pygame.transform.smoothscale(personajes[(p_i - 1) % len(personajes)], (side_size, side_size))
        nxt  = pygame.transform.smoothscale(personajes[(p_i + 1) % len(personajes)], (side_size, side_size))

        pantalla.blit(prev, prev.get_rect(center=(centro_x_p - offset_p, centro_y)))
        pantalla.blit(main, main.get_rect(center=(centro_x_p, centro_y)))
        pantalla.blit(nxt,  nxt.get_rect(center=(centro_x_p + offset_p, centro_y)))

        # =========================
        # FONDOS (CARRUSEL)
        # =========================
        centro_x_f = 3 * ANCHO // 4
        offset_f = 110

        bg_main_size = (160, 110)
        bg_side_size = (120, 80)

        bg_main = pygame.transform.smoothscale(fondos[f_i], bg_main_size)
        bg_prev = pygame.transform.smoothscale(fondos[(f_i - 1) % len(fondos)], bg_side_size)
        bg_next = pygame.transform.smoothscale(fondos[(f_i + 1) % len(fondos)], bg_side_size)

        pantalla.blit(bg_prev, bg_prev.get_rect(center=(centro_x_f - offset_f, centro_y)))
        pantalla.blit(bg_main, bg_main.get_rect(center=(centro_x_f, centro_y)))
        pantalla.blit(bg_next, bg_next.get_rect(center=(centro_x_f + offset_f, centro_y)))

        pygame.display.update()
        reloj.tick(60)