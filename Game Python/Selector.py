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

    while True:

        mando.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if cooldown > 0:
            cooldown -= 1

        move_p = mando.selector_personaje()
        move_f = mando.selector_fondo()

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

        if keys[pygame.K_RETURN] or mando.A():
            pygame.event.clear()
            return personajes[p_i], fondos[f_i]

        if mando.B():
            pygame.quit()
            sys.exit()

        pantalla.fill((20,20,20))

        legend = [
            "Selecciona personaje y fondo",
            "A / joystick izq personaje | S / joystick der fondo",
            "ENTER / A jugar"
        ]

        for i, line in enumerate(legend):
            txt = fuente_small.render(line, True, (220,220,220))
            pantalla.blit(txt, (ANCHO//2 - txt.get_width()//2, 30 + i*22))

        # personaje
        main = pygame.transform.smoothscale(personajes[p_i], (90,90))
        prev = pygame.transform.smoothscale(personajes[(p_i-1)%len(personajes)], (60,60))
        nxt  = pygame.transform.smoothscale(personajes[(p_i+1)%len(personajes)], (60,60))

        pantalla.blit(prev, prev.get_rect(center=(ANCHO//4 - 100, ALTO//2)))
        pantalla.blit(main, main.get_rect(center=(ANCHO//4, ALTO//2)))
        pantalla.blit(nxt, nxt.get_rect(center=(ANCHO//4 + 100, ALTO//2)))

        # fondo
        bg_main = pygame.transform.smoothscale(fondos[f_i], (160,110))
        bg_prev = pygame.transform.smoothscale(fondos[(f_i-1)%len(fondos)], (120,80))
        bg_next = pygame.transform.smoothscale(fondos[(f_i+1)%len(fondos)], (120,80))

        pantalla.blit(bg_prev, bg_prev.get_rect(center=(3*ANCHO//4 - 120, ALTO//2)))
        pantalla.blit(bg_main, bg_main.get_rect(center=(3*ANCHO//4, ALTO//2)))
        pantalla.blit(bg_next, bg_next.get_rect(center=(3*ANCHO//4 + 120, ALTO//2)))

        pygame.display.update()
        reloj.tick(60)