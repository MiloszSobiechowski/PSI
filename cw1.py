import sys
import time
import os
from collections import deque

# Kolory terminala
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

# Kierunki ruchu
DIRECTIONS = {
    '↑': (-1, 0),
    '↓': (1, 0),
    '→': (0, 1),
    '←': (0, -1)
}

# Definicje pól i możliwych kierunków ruchu
CELL_CONNECTIONS = {
    '┼': ['↑', '↓', '→', '←'],
    '│': ['↑', '↓'],
    '─': ['→', '←'],
    '┌': ['↓', '→'],
    '┐': ['↓', '←'],
    '┘': ['↑', '←'],
    '└': ['↑', '→'],
    '┬': ['↓', '→', '←'],
    '┴': ['↑', '→', '←'],
    '├': ['↑', '↓', '→'],
    '┤': ['↑', '↓', '←'],
    '╵': ['↑'],
    '╷': ['↓'],
    '╴': ['←'],
    '╶': ['→'],
    ' ': []
}


def read_map(path):
    with open(path, encoding='utf-8') as f:
        lines = [list(line.rstrip('\n')) for line in f.readlines()]
    max_len = max(len(l) for l in lines)
    for l in lines:
        while len(l) < max_len:
            l.append(' ')
    return lines


def draw_map(lab, visited=set(), queue=set(), start=None, end=None):
    for i, row in enumerate(lab):
        for j, cell in enumerate(row):
            char = cell
            pos = (i, j)
            if pos == start:
                print(RED + char + RESET, end='')
            elif pos == end:
                print(BLUE + char + RESET, end='')
            elif pos in visited:
                print(GREEN + char + RESET, end='')
            elif pos in queue:
                print(YELLOW + char + RESET, end='')
            else:
                print(char, end='')
        print()
    time.sleep(0.1)


def valid_move(lab, x, y, nx, ny, dx, dy):
    """Sprawdza, czy można przejść z (x,y) do (nx,ny)"""
    if not (0 <= nx < len(lab) and 0 <= ny < len(lab[0])):
        return False
    curr = lab[x][y]
    nextc = lab[nx][ny]
    if curr not in CELL_CONNECTIONS or nextc not in CELL_CONNECTIONS:
        return False

    # Kierunek ruchu i odwrotny kierunek
    move_dir = None
    for d, (ddx, ddy) in DIRECTIONS.items():
        if (dx, dy) == (ddx, ddy):
            move_dir = d
            break
    opposite = {'↑': '↓', '↓': '↑', '→': '←', '←': '→'}[move_dir]

    return move_dir in CELL_CONNECTIONS[curr] and opposite in CELL_CONNECTIONS[nextc]


def search(lab, start, end, algorithm='BFS'):
    visited = set()
    queue = deque([(start, [start])])
    steps = 0

    while queue:
        draw_map(lab, visited, {p for p, _ in queue}, start, end)
        if algorithm.upper() == 'DFS':
            pos, path = queue.pop()
        else:
            pos, path = queue.popleft()

        steps += 1
        if pos == end:
            draw_map(lab, visited, set(), start, end)
            print(GREEN + f"\nZnaleziono ścieżkę! Kroki: {steps}" + RESET)
            return path

        if pos in visited:
            continue

        visited.add(pos)
        x, y = pos
        for d, (dx, dy) in DIRECTIONS.items():
            nx, ny = x + dx, y + dy
            if valid_move(lab, x, y, nx, ny, dx, dy) and (nx, ny) not in visited:
                queue.append(((nx, ny), path + [(nx, ny)]))

    draw_map(lab, visited, set(), start, end)
    print(RED + f"\nNie znaleziono ścieżki po {steps} krokach." + RESET)
    return None


def main():
    if len(sys.argv) != 2:
        print("Użycie: python labirynt.py <ścieżka_do_mapy>")
        return

    path = sys.argv[1]
    lab = read_map(path)
    draw_map(lab)

    start = tuple(map(int, input("Podaj współrzędne startowe (wiersz kolumna): ").split()))
    end = tuple(map(int, input("Podaj współrzędne końcowe (wiersz kolumna): ").split()))
    alg = input("Wybierz algorytm (BFS/DFS): ").strip().upper()
    if alg not in ('BFS', 'DFS'):
        alg = 'BFS'

    search(lab, start, end, alg)


if __name__ == "__main__":
    main()
