import math

PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = ' '

MAX_DEPTH_INF = float('inf')

class TicTacToe:
    def __init__(self, size=3):
        if size < 3:
            raise ValueError("Rozmiar planszy musi być co najmniej 3x3.")
        self.size = size
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.current_player = PLAYER_X

    def display_board(self):
        print(f"\n--- Aktualna Plansza ({self.size}x{self.size}) ---")
        for row in self.board:
            print('| ' + ' | '.join(row) + ' |')
            print('-' + '----' * self.size)
        print("------------------------" + ('----' * (self.size - 3)) + "\n")

    def is_valid_move(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == EMPTY

    def make_move(self, row, col, player):
        self.board[row][col] = player

    def get_winner(self):
        
        for i in range(self.size):
            if self.board[i][0] != EMPTY and all(self.board[i][j] == self.board[i][0] for j in range(self.size)):
                return self.board[i][0]
            if self.board[0][i] != EMPTY and all(self.board[j][i] == self.board[0][i] for j in range(self.size)):
                return self.board[0][i]

        if self.board[0][0] != EMPTY and all(self.board[i][i] == self.board[0][0] for i in range(self.size)):
            return self.board[0][0]
        if self.board[0][self.size-1] != EMPTY and all(self.board[i][self.size-1-i] == self.board[0][self.size-1] for i in range(self.size)):
            return self.board[0][self.size-1]
        
        return None

    def is_board_full(self):
        return all(self.board[i][j] != EMPTY for i in range(self.size) for j in range(self.size))

    def is_terminal(self):
        return self.get_winner() is not None or self.is_board_full()

def minimax(game, depth, is_maximizing_player, max_depth):
    
    winner = game.get_winner()
    if winner == PLAYER_O:
        return 10 + depth
    elif winner == PLAYER_X:
        return -10 - depth
    elif game.is_board_full():
        return 0
    
    if depth == max_depth: 
        return 0

    if is_maximizing_player:
        max_eval = -math.inf
        for r in range(game.size):
            for c in range(game.size):
                if game.is_valid_move(r, c):
                    game.make_move(r, c, PLAYER_O)
                    eval = minimax(game, depth + 1, False, max_depth)
                    game.make_move(r, c, EMPTY)
                    max_eval = max(max_eval, eval)
        return max_eval

    else:
        min_eval = math.inf
        for r in range(game.size):
            for c in range(game.size):
                if game.is_valid_move(r, c):
                    game.make_move(r, c, PLAYER_X)
                    eval = minimax(game, depth + 1, True, max_depth)
                    game.make_move(r, c, EMPTY)
                    min_eval = min(min_eval, eval)
        return min_eval

def find_best_move(game, max_depth):
    best_eval = -math.inf
    best_move = None
    
    for r in range(game.size):
        for c in range(game.size):
            if game.is_valid_move(r, c):
                
                game.make_move(r, c, PLAYER_O)
                
                eval = minimax(game, 0, False, max_depth)
                
                game.make_move(r, c, EMPTY)

                if eval > best_eval:
                    best_eval = eval
                    best_move = (r, c)
    
    return best_move

def play_game():

    print("Witaj w Kółku i Krzyżyk (Minimax AI)")
    
    try:
        board_size_input = input(f"Podaj rozmiar planszy (np. 3 dla 3x3, minimum 3, domyślnie 3): ")
        
        try:
            board_size = int(board_size_input) if board_size_input.strip() else 3
            if board_size < 3:
                print("Rozmiar musi być co najmniej 3. Używam domyślnego 3x3.")
                board_size = 3
        except ValueError:
             print("Nieprawidłowa wartość. Używam domyślnego 3x3.")
             board_size = 3

        default_depth = MAX_DEPTH_INF 
        if board_size > 3:
            default_depth = 4 
            print(f"\nINFO: Plansza {board_size}x{board_size} jest duża.")
            print(f"Używamy domyślnego limitu głębokości Minimax: {default_depth} (dla optymalizacji czasu).")
        
        depth_label = 'bez limitu' if default_depth == MAX_DEPTH_INF else str(int(default_depth))
        depth_input = input(f"Podaj max głębokość algorytmu Minimax (domyślnie: {depth_label}): ")
        
        if depth_input.isdigit() and int(depth_input) >= 0:
            max_depth = int(depth_input)
        else:
            max_depth = default_depth

        first_player_input = input("Kto zaczyna? (Ty / Komputer, domyślnie: Ty): ").lower().strip()
        
        user_char = PLAYER_X
        comp_char = PLAYER_O
        
        if first_player_input.startswith('k'):
            current_turn = comp_char
            print("Zaczyna Komputer (O).")
        else:
            current_turn = user_char
            print("Zaczynasz Ty (X).")

        game = TicTacToe(size=board_size)

    except ValueError as e:
        print(f"Błąd konfiguracji: {e}")
        return

    while not game.is_terminal():
        game.display_board()

        if current_turn == user_char:
            while True:
                try:
                    move_str = input(f"Twój ruch ({user_char}). Podaj wiersz i kolumnę (0-{board_size-1}, np. 1 2): ").strip().split()
                    row, col = int(move_str[0]), int(move_str[1])
                    if game.is_valid_move(row, col):
                        game.make_move(row, col, user_char)
                        break
                    else:
                        print(f"Nieprawidłowy ruch. Wiersz i kolumna muszą być w zakresie 0 do {board_size-1}, a pole musi być puste.")
                except (IndexError, ValueError):
                    print("Nieprawidłowy format. Podaj dwie liczby oddzielone spacją (np. 0 1).")
            
            current_turn = comp_char

        else:
            depth_info = "pełna" if max_depth == MAX_DEPTH_INF else f"{int(max_depth)}"
            print(f"Ruch Komputera ({comp_char}). Analizuję (Głębokość: {depth_info})...")
            
            comp_move = find_best_move(game, max_depth)
            
            if comp_move:
                row, col = comp_move
                game.make_move(row, col, comp_char)
                print(f"Komputer zagrał wiersz {row}, kolumna {col}.")
            else:
                print("Błąd: Komputer nie znalazł ruchu.")
                break 

            current_turn = user_char

    game.display_board()
    winner = game.get_winner()
    
    if winner == user_char:
        print("Wygrałeś!")
    elif winner == comp_char:
        print("Wygrywa Komputer!")
    else:
        print("Remis!")


if __name__ == "__main__":
    play_game()