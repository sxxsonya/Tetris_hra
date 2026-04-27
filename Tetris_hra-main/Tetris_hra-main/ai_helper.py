import copy
from settings import ROWS, COLUMNS

class AIHelper:
    def __init__(self):
        pass

    def get_best_move(self, grid, piece):
        best_score = -float('inf')
        best_x = piece.x
        best_shape = piece.shape

        # Zkusíme 4 rotace (nebo méně, záleží na tvaru, ale pro jednoduchost zkusíme 4)
        current_shape = piece.shape
        for _ in range(4):
            # Zkusíme všechny sloupce
            for x in range(-2, COLUMNS):
                temp_piece = piece.clone()
                temp_piece.shape = current_shape
                temp_piece.x = x
                
                # Zkontrolujeme, jestli je vůbec na platné pozici nahoře
                if not self.check_collision(grid, temp_piece):
                    # Spustíme dílek dolů
                    drop_y = self.get_drop_y(grid, temp_piece)
                    temp_piece.y = drop_y
                    
                    # Ohodnotíme stav desky po dopadu
                    score = self.evaluate_board(grid, temp_piece)
                    
                    if score > best_score:
                        best_score = score
                        best_x = x
                        best_shape = current_shape
            
            # Otočíme pro další iteraci
            current_shape = [list(row) for row in zip(*current_shape[::-1])]

        return best_x, best_shape

    def check_collision(self, grid, piece, dx=0, dy=0):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = piece.x + x + dx
                    ny = piece.y + y + dy
                    if nx < 0 or nx >= COLUMNS or ny >= ROWS:
                        return True
                    if ny >= 0 and grid[ny][nx]:
                        return True
        return False

    def get_drop_y(self, grid, piece):
        ghost_y = piece.y
        while not self.check_collision(grid, piece, dy=(ghost_y - piece.y) + 1):
            ghost_y += 1
        return ghost_y

    def evaluate_board(self, grid, piece):
        # Nasimulujeme vložení dílku
        temp_grid = copy.deepcopy(grid)
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    ny = piece.y + y
                    nx = piece.x + x
                    if 0 <= ny < ROWS:
                        temp_grid[ny][nx] = 1

        holes = 0
        lines = 0
        aggregate_height = 0

        # Kontrola řad a výšky
        for y in range(ROWS):
            if all(temp_grid[y]):
                lines += 1
        
        for x in range(COLUMNS):
            col_height = 0
            block_found = False
            for y in range(ROWS):
                if temp_grid[y][x]:
                    if not block_found:
                        col_height = ROWS - y
                        block_found = True
                elif block_found:
                    holes += 1 # Pokud je prázdno pod blokem, je to díra
            aggregate_height += col_height

        # Heuristika: Chceme čistit řady, nechceme díry a nechceme stavět moc vysoko
        score = (lines * 100) - (holes * 50) - (aggregate_height * 10)
        return int(score)