import pygame
import sys


def selector(pantalla, reloj, mando, personajes, fondos):
    pygame.event.clear()
    mando.update()

    ancho, alto = pantalla.get_size()

    fuente_titulo = pygame.font.SysFont(None, 44)
    fuente_small = pygame.font.SysFont(None, 24)

    p_i = 0
    f_i = 0
    fase = "personaje"
    cooldown = 0
    input_lock = 20  # evita auto-input al entrar

    while True:
        mando.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if input_lock > 0:
            input_lock -= 1
        else:
            if cooldown > 0:
                cooldown -= 1

            move_p = mando.selector_personaje()
            move_f = mando.selector_fondo()

            if cooldown == 0:
                if fase == "personaje":
                    if keys[pygame.K_LEFT] or move_p == "LEFT":
                        p_i = (p_i - 1) % len(personajes)
                        cooldown = 8
                    elif keys[pygame.K_RIGHT] or move_p == "RIGHT":
                        p_i = (p_i + 1) % len(personajes)
                        cooldown = 8
                else:
                    if keys[pygame.K_LEFT] or keys[pygame.K_a] or move_f == "LEFT":
                        f_i = (f_i - 1) % len(fondos)
                        cooldown = 8
                    elif keys[pygame.K_RIGHT] or keys[pygame.K_d] or move_f == "RIGHT":
                        f_i = (f_i + 1) % len(fondos)
                        cooldown = 8

            if keys[pygame.K_RETURN] or mando.A():
                pygame.event.clear()
                if fase == "personaje":
                    fase = "fondo"
                    cooldown = 8
                    input_lock = 12
                else:
                    return personajes[p_i], fondos[f_i]

            if mando.B():
                pygame.event.clear()
                if fase == "fondo":
                    fase = "personaje"
                    cooldown = 8
                    input_lock = 12
                else:
                    pygame.quit()
                    sys.exit()

        pantalla.fill((20, 20, 20))

        if fase == "personaje":
            titulo = fuente_titulo.render("1/2 Selecciona personaje", True, (245, 245, 245))
            ayuda_1 = fuente_small.render("Flechas o cruceta: mover", True, (220, 220, 220))
            ayuda_2 = fuente_small.render("A o ENTER: confirmar personaje", True, (220, 220, 220))
            ayuda_3 = fuente_small.render("B: salir", True, (220, 220, 220))

            pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, 52)))
            pantalla.blit(ayuda_1, ayuda_1.get_rect(center=(ancho // 2, 92)))
            pantalla.blit(ayuda_2, ayuda_2.get_rect(center=(ancho // 2, 116)))
            pantalla.blit(ayuda_3, ayuda_3.get_rect(center=(ancho // 2, 140)))

            centro_x = ancho // 2
            centro_y = alto // 2 + 40
            offset = 130
            main_size = 130
            side_size = 84

            main = pygame.transform.smoothscale(personajes[p_i], (main_size, main_size))
            prev = pygame.transform.smoothscale(personajes[(p_i - 1) % len(personajes)], (side_size, side_size))
            nxt = pygame.transform.smoothscale(personajes[(p_i + 1) % len(personajes)], (side_size, side_size))

            pantalla.blit(prev, prev.get_rect(center=(centro_x - offset, centro_y)))
            pantalla.blit(main, main.get_rect(center=(centro_x, centro_y)))
            pantalla.blit(nxt, nxt.get_rect(center=(centro_x + offset, centro_y)))
        else:
            titulo = fuente_titulo.render("2/2 Selecciona paisaje", True, (245, 245, 245))
            ayuda_1 = fuente_small.render("Flechas, A/D o cruceta: mover", True, (220, 220, 220))
            ayuda_2 = fuente_small.render("A o ENTER: jugar", True, (220, 220, 220))
            ayuda_3 = fuente_small.render("B: volver a personaje", True, (220, 220, 220))

            pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, 52)))
            pantalla.blit(ayuda_1, ayuda_1.get_rect(center=(ancho // 2, 92)))
            pantalla.blit(ayuda_2, ayuda_2.get_rect(center=(ancho // 2, 116)))
            pantalla.blit(ayuda_3, ayuda_3.get_rect(center=(ancho // 2, 140)))

            elegido = pygame.transform.smoothscale(personajes[p_i], (70, 70))
            pantalla.blit(elegido, elegido.get_rect(center=(ancho // 2, 195)))

            centro_x = ancho // 2
            centro_y = alto // 2 + 55
            offset = 188
            bg_main_size = (260, 170)
            bg_side_size = (170, 110)

            bg_main = pygame.transform.smoothscale(fondos[f_i], bg_main_size)
            bg_prev = pygame.transform.smoothscale(fondos[(f_i - 1) % len(fondos)], bg_side_size)
            bg_next = pygame.transform.smoothscale(fondos[(f_i + 1) % len(fondos)], bg_side_size)

            pantalla.blit(bg_prev, bg_prev.get_rect(center=(centro_x - offset, centro_y)))
            pantalla.blit(bg_main, bg_main.get_rect(center=(centro_x, centro_y)))
            pantalla.blit(bg_next, bg_next.get_rect(center=(centro_x + offset, centro_y)))

        pygame.display.update()
        reloj.tick(60)
