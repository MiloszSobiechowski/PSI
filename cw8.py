import numpy as np
import matplotlib.pyplot as plt
import random


dane = [
    [-3, -4, -1],
    [-2,  1, -1],
    [ 0,  1, -1],
    [ 2,  2, -1],
    [-2, -4,  1],
    [ 0, -2,  1],
    [ 2,  1,  1],
    [ 3, -4,  1]
]

wagi = np.zeros(3)
wspolcz = 0.1
epoki = 100

plt.ion()

for e in range(epoki):
    random.shuffle(dane)
    bledy = 0
    
    for row in dane:
        x1, x2, cel = row
        x = np.array([1, x1, x2])
        
        suma = np.dot(wagi, x)
        
        y = 1 if suma >= 0 else -1
        
        if y != cel:
            blad = cel - y
            wagi = wagi + wspolcz * blad * x
            bledy += 1

    plt.clf()
    plt.title(f"Epoka: {e+1}, Błędy: {bledy}")
    plt.grid(True)
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)

    for d in dane:
        kolor = 'blue' if d[2] == 1 else 'red'
        znak = 'o' if d[2] == 1 else 'x'
        plt.scatter(d[0], d[1], c=kolor, marker=znak)

    xx = np.linspace(-5, 5, 100)
    if wagi[2] != 0:
        yy = -(wagi[1]*xx + wagi[0]) / wagi[2]
        plt.plot(xx, yy, 'g--')
    
    plt.pause(0.2)

    if bledy == 0:
        print("Koniec nauki!")
        print(f"Znalezione wagi: {wagi}")
        break

plt.ioff()
plt.show()