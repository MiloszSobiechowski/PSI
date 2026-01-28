import pygame
import random
import math


W, H = 1000, 800
N = 50 
PREDKOSC = 4
MAX_SILA = 0.1      
KAT_WIDZENIA = 120
K_SASIADOW = 5      
PROMIEN = 100       

pygame.init()
ekran = pygame.display.set_mode((W, H))
zegar = pygame.time.Clock()

boidy = [[random.randint(0, W), random.randint(0, H), random.uniform(-1, 1), random.uniform(-1, 1)] for _ in range(N)]

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: run = False

    ekran.fill((30, 30, 30))
    nowe_dane = []

    for b in boidy:
        x, y, vx, vy = b
        
        widziani = []
        for inny in boidy:
            if inny == b: continue
            dx, dy = inny[0]-x, inny[1]-y
            dist = (dx**2 + dy**2)**0.5
            
            if dist < PROMIEN:
                kat_boida = math.atan2(vy, vx)
                kat_do_innego = math.atan2(dy, dx)
                roznica = abs(math.degrees(kat_do_innego - kat_boida))
                if roznica > 180: roznica = 360 - roznica
                
                if roznica < KAT_WIDZENIA / 2:
                    widziani.append((dist, inny))
        
        widziani.sort(key=lambda s: s[0])
        sasiedzi = [s[1] for s in widziani[:K_SASIADOW]]

        ax, ay = 0, 0
        
        if sasiedzi:
            avg_x = sum(s[0] for s in sasiedzi) / len(sasiedzi)
            avg_y = sum(s[1] for s in sasiedzi) / len(sasiedzi)
            avg_vx = sum(s[2] for s in sasiedzi) / len(sasiedzi)
            avg_vy = sum(s[3] for s in sasiedzi) / len(sasiedzi)

            ax += (avg_x - x) * 0.02
            ay += (avg_y - y) * 0.02
            ax += (avg_vx - vx) * 0.1
            ay += (avg_vy - vy) * 0.1
            for s in sasiedzi:
                d = ((s[0]-x)**2 + (s[1]-y)**2)**0.5
                if d < 25:
                    ax -= (s[0] - x) * 0.1
                    ay -= (s[1] - y) * 0.1

        sila = (ax**2 + ay**2)**0.5
        if sila > MAX_SILA:
            ax, ay = (ax/sila)*MAX_SILA, (ay/sila)*MAX_SILA

        vx += ax; vy += ay
        mag = (vx**2 + vy**2)**0.5
        vx, vy = (vx/mag)*PREDKOSC, (vy/mag)*PREDKOSC
        
        nowe_dane.append([(x + vx) % W, (y + vy) % H, vx, vy])

    boidy = nowe_dane

    for b in boidy:
        kat = math.atan2(b[3], b[2])
        p1 = (b[0] + math.cos(kat)*10, b[1] + math.sin(kat)*10)
        p2 = (b[0] + math.cos(kat+2.5)*6, b[1] + math.sin(kat+2.5)*6)
        p3 = (b[0] + math.cos(kat-2.5)*6, b[1] + math.sin(kat-2.5)*6)
        pygame.draw.polygon(ekran, (0, 255, 0), [p1, p2, p3])

    pygame.display.flip()
    zegar.tick(60)
pygame.quit()