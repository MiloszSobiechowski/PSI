import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def funkcja_gaussa(x, mu, sigma):
    potega = -((x - mu) ** 2) / (2 * (sigma ** 2))
    return math.exp(potega)

class SterownikNawilzacza:
    def __init__(self, cena_pradu):
        self.cena_pradu = cena_pradu

    def oblicz_moc(self, wilgotnosc, temperatura):
        wilg_niska = funkcja_gaussa(wilgotnosc, 0, 25)
        wilg_optymalna = funkcja_gaussa(wilgotnosc, 50, 15)
        wilg_wysoka = funkcja_gaussa(wilgotnosc, 100, 25)

        temp_zimno = funkcja_gaussa(temperatura, 10, 10)
        temp_cieplo = funkcja_gaussa(temperatura, 30, 10)

        wspolczynnik_ceny = 1.0 - (self.cena_pradu * 0.4)

        reguly = []

        r1_aktywacja = wilg_niska * temp_zimno
        r1_wynik = 90 * wspolczynnik_ceny
        reguly.append((r1_aktywacja, r1_wynik))

        r2_aktywacja = wilg_niska * temp_cieplo
        r2_wynik = 100 * wspolczynnik_ceny
        reguly.append((r2_aktywacja, r2_wynik))

        r3_aktywacja = wilg_optymalna
        r3_wynik = 40 * wspolczynnik_ceny
        reguly.append((r3_aktywacja, r3_wynik))

        r4_aktywacja = wilg_wysoka
        r4_wynik = 0
        reguly.append((r4_aktywacja, r4_wynik))

        licznik = 0.0
        mianownik = 0.0
        
        for aktywacja, wynik in reguly:
            licznik += aktywacja * wynik
            mianownik += aktywacja
        
        if mianownik == 0:
            return 0.0
            
        return licznik / mianownik

cena = 0.5
sterownik = SterownikNawilzacza(cena)

zakres_wilg = [i for i in range(0, 101, 2)]
zakres_temp = [i for i in range(10, 31, 1)]

X = []
Y = []
Z = []

for w in zakres_wilg:
    for t in zakres_temp:
        moc = sterownik.oblicz_moc(w, t)
        X.append(w)
        Y.append(t)
        Z.append(moc)

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

ax.plot_trisurf(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.9)

ax.set_xlabel('Wilgotnosc (%)')
ax.set_ylabel('Temperatura (C)')
ax.set_zlabel('Moc nawilzania (%)')
ax.set_title(f'Charakterystyka Sterownika (Cena pradu: {cena})')

ax.view_init(elev=30, azim=135)

plt.show()