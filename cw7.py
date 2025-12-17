import math
import random
from ucimlrepo import fetch_ucirepo

def odleglosc_euklidesowa(p1, p2):
    suma = 0.0
    for i in range(len(p1)):
        roznica = p1[i] - p2[i]
        suma += roznica ** 2
    return math.sqrt(suma)

def odleglosc_manhattan(p1, p2):
    suma = 0.0
    for i in range(len(p1)):
        suma += abs(p1[i] - p2[i])
    return suma

def normalizuj_dane(dane):
    min_cechy = list(dane[0])
    max_cechy = list(dane[0])
    
    for wiersz in dane:
        for i in range(len(wiersz)):
            if wiersz[i] < min_cechy[i]:
                min_cechy[i] = wiersz[i]
            if wiersz[i] > max_cechy[i]:
                max_cechy[i] = wiersz[i]

    dane_znormalizowane = []
    for wiersz in dane:
        nowy_wiersz = []
        for i in range(len(wiersz)):
            zakres = max_cechy[i] - min_cechy[i]
            if zakres == 0:
                nowy_wiersz.append(0.0)
            else:
                wartosc = (wiersz[i] - min_cechy[i]) / zakres
                nowy_wiersz.append(wartosc)
        dane_znormalizowane.append(nowy_wiersz)
        
    return dane_znormalizowane

def znajdz_sasiadow(X_treningowe, y_treningowe, nowy_punkt, k, metryka):
    odleglosci = []
    for i in range(len(X_treningowe)):
        punkt_treningowy = X_treningowe[i]
        klasa = y_treningowe[i]
        
        if metryka == 'Euklidesowa':
            dist = odleglosc_euklidesowa(nowy_punkt, punkt_treningowy)
        else:
            dist = odleglosc_manhattan(nowy_punkt, punkt_treningowy)
            
        odleglosci.append([dist, klasa])
    
    odleglosci.sort(key=lambda x: x[0])
    
    najblizsi_sasiedzi = []
    for i in range(k):
        najblizsi_sasiedzi.append(odleglosci[i][1])
        
    return najblizsi_sasiedzi

def przewidz_klase(sasiedzi):
    glosy = {}
    for klasa in sasiedzi:
        klasa_str = str(klasa)
        if klasa_str in glosy:
            glosy[klasa_str] += 1
        else:
            glosy[klasa_str] = 1
            
    najczestsza_klasa = None
    max_glosow = -1
    
    for klasa in glosy:
        if glosy[klasa] > max_glosow:
            max_glosow = glosy[klasa]
            najczestsza_klasa = klasa
            
    return najczestsza_klasa

def zrob_zadanie(nazwa, X_pandas, y_pandas):
    print(f"\n=== ZBIÓR: {nazwa} ===")
    
    X = X_pandas.values.tolist()
    y_temp = y_pandas.values.tolist()
    
    y = []
    for element in y_temp:
        if isinstance(element, list):
            y.append(element[0])
        else:
            y.append(element)
    
    dane_razem = []
    for i in range(len(X)):
        wiersz = list(X[i])
        wiersz.append(y[i])
        dane_razem.append(wiersz)
    
    random.seed(42)
    random.shuffle(dane_razem)
    
    ilosc = len(dane_razem)
    podzial = int(ilosc * 0.6)
    
    trening = dane_razem[:podzial]
    test = dane_razem[podzial:]
    
    X_trening_surowe = []
    y_trening = []
    for wiersz in trening:
        X_trening_surowe.append(wiersz[:-1])
        y_trening.append(wiersz[-1])
        
    X_test_surowe = []
    y_test = []
    for wiersz in test:
        X_test_surowe.append(wiersz[:-1])
        y_test.append(wiersz[-1])

    wszystkie_X = X_trening_surowe + X_test_surowe
    X_znormalizowane = normalizuj_dane(wszystkie_X)
    
    X_trening = X_znormalizowane[:len(X_trening_surowe)]
    X_test = X_znormalizowane[len(X_trening_surowe):]
    
    lista_k = [1, 5, 10]
    metryki = ['Euklidesowa', 'Manhattan']
    
    print("Metryka       |  k  | Dokładność")
    print("-" * 30)
    
    for metryka in metryki:
        for k in lista_k:
            dobre_trafienia = 0
            for i in range(len(X_test)):
                sasiedzi = znajdz_sasiadow(X_trening, y_trening, X_test[i], k, metryka)
                wynik = str(przewidz_klase(sasiedzi))
                oczekiwany = str(y_test[i])
                
                if wynik == oczekiwany:
                    dobre_trafienia += 1
            
            procent = (dobre_trafienia / len(X_test)) * 100
            print(f"{metryka:<13} | {k:<3} | {procent:.2f}%")

try:
    print("Pobieranie Iris...")
    iris = fetch_ucirepo(id=53) 
    
    zrob_zadanie("IRIS", iris.data.features, iris.data.targets)
except Exception as e:
    print("Błąd z Iris:", e)

try:
    print("\nPobieranie Wine...")
    wine = fetch_ucirepo(id=109) 
    
    zrob_zadanie("WINE", wine.data.features, wine.data.targets)
except Exception as e:
    print("Błąd z Wine:", e)