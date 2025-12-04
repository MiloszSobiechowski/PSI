import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sympy as sp
import random
import math

def przygotuj_wzor(napis_wzoru):
    x = sp.symbols('x')
    mapowanie = {'sin': sp.sin, 'cos': sp.cos, 'pi': sp.pi, 'exp': sp.exp, 'abs': sp.Abs}
    
    wyrazenie = sp.sympify(napis_wzoru, locals=mapowanie)
    
    funkcja_do_wykresu = sp.lambdify(x, wyrazenie, modules=['numpy'])
    funkcja_zwykla = sp.lambdify(x, wyrazenie, modules=['math'])
    
    return funkcja_do_wykresu, funkcja_zwykla

def szukaj_ekstremum(funkcja, start_x, zakres, tryb, algorytm, chlodzenie='geo'):
    sciezka = [start_x]
    obecny_x = start_x
    temperatura = 10.0
    
    liczba_krokow = 200
    wielkosc_kroku = 0.5

    for i in range(liczba_krokow):
        losowe_przesuniecie = random.uniform(-wielkosc_kroku, wielkosc_kroku)
        nowy_x = obecny_x + losowe_przesuniecie
        nowy_x = max(zakres[0], min(nowy_x, zakres[1]))
        
        wartosc_obecna = funkcja(obecny_x)
        wartosc_nowa = funkcja(nowy_x)
        
        roznica = wartosc_nowa - wartosc_obecna
        if tryb == 'max':
            roznica = -roznica

        czy_akceptujemy = False

        if roznica < 0:
            czy_akceptujemy = True
        else:
            if algorytm == 'wyzarzanie':
                szansa = math.exp(-roznica / temperatura)
                if random.random() < szansa:
                    czy_akceptujemy = True

        if czy_akceptujemy:
            obecny_x = nowy_x

        sciezka.append(obecny_x)

        if algorytm == 'wyzarzanie':
            if chlodzenie == 'geo':
                temperatura = temperatura * 0.95
            else:
                temperatura = temperatura - (10.0 / liczba_krokow)
            
            if temperatura < 0.001:
                temperatura = 0.001

    return sciezka

wzor_tekst = input("Wzór funkcji (Enter = domyślny): ")
if not wzor_tekst:
    wzor_tekst = "x**2 - 10*cos(2*pi*x) + x/5"

tryb = input("Szukamy min czy max? (Enter = min): ")
if tryb != 'max': tryb = 'min'

wybor_algorytmu = input("Algorytm: 1=Hill Climbing, 2=Wyżarzanie: ")
algorytm = 'wyzarzanie' if wybor_algorytmu == '2' else 'hill'

typ_chlodzenia = 'geo'
if algorytm == 'wyzarzanie':
    wybor_chlodzenia = input("Chłodzenie: 1=Geo, 2=Liniowe: ")
    if wybor_chlodzenia == '2': typ_chlodzenia = 'lin'

f_wykres, f_obliczenia = przygotuj_wzor(wzor_tekst)

start_x = random.uniform(-5, 5)
historia_ruchow = szukaj_ekstremum(f_obliczenia, start_x, [-5, 5], tryb, algorytm, typ_chlodzenia)

print(f"Znaleziono x: {historia_ruchow[-1]:.4f}")

fig, ax = plt.subplots()
x_tlo = np.linspace(-5, 5, 400)
ax.plot(x_tlo, f_wykres(x_tlo), label='Funkcja')
kropka, = ax.plot([], [], 'ro', markersize=10, label='Algorytm')

ax.set_title(f"Algorytm: {algorytm.upper()}")
ax.legend()
ax.grid(True)

def aktualizuj_klatke(numer_kroku):
    x = historia_ruchow[numer_kroku]
    y = f_obliczenia(x)
    kropka.set_data([x], [y])
    return kropka,

ani = animation.FuncAnimation(fig, aktualizuj_klatke, 
                              frames=len(historia_ruchow), 
                              interval=30, blit=True)

plt.show()
