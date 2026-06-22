from constants import (
    BOARD_ROWS, BOARD_COLS, RED, BLACK,
    INITIAL_BOARD, PIECE_NAMES, PIECE_VALUES,
    PAWN_BONUS_RED, PAWN_BONUS_BLACK
)
import copy


class Board:
    def __init__(self, board_state=None):
        if board_state is None:
            self.board = copy.deepcopy(INITIAL_BOARD)
        else:
            self.board = copy.deepcopy(board_state)
        self.current_player = RED
        self.move_history = []

    def get_piece(self, row, col):
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return self.board[row][col]
        return None

    def get_piece_color(self, piece):
        if not piece:
            return None
        return RED if piece[0] == 'r' else BLACK

    def get_piece_type(self, piece):
        if not piece:
            return None
        return piece[1]

    def is_valid_position(self, row, col):
        return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS

    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''
        self.move_history.append((from_row, from_col, to_row, to_col, captured))
        self.current_player = BLACK if self.current_player == RED else RED
        return captured

    def undo_move(self):
        if not self.move_history:
            return False
        from_row, from_col, to_row, to_col, captured = self.move_history.pop()
        piece = self.board[to_row][to_col]
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured
        self.current_player = BLACK if self.current_player == RED else RED
        return True

    def get_all_moves(self, color):
        moves = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and self.get_piece_color(piece) == color:
                    piece_moves = self.get_piece_moves(row, col)
                    for (to_row, to_col) in piece_moves:
                        moves.append((row, col, to_row, to_col))
        return moves

    def get_piece_moves(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return []
        piece_type = self.get_piece_type(piece)
        color = self.get_piece_color(piece)
        moves = []

        if piece_type == 'K':
            moves = self._king_moves(row, col, color)
        elif piece_type == 'A':
            moves = self._advisor_moves(row, col, color)
        elif piece_type == 'B':
            moves = self._elephant_moves(row, col, color)
        elif piece_type == 'N':
            moves = self._horse_moves(row, col, color)
        elif piece_type == 'R':
            moves = self._rook_moves(row, col, color)
        elif piece_type == 'C':
            moves = self._cannon_moves(row, col, color)
        elif piece_type == 'P':
            moves = self._pawn_moves(row, col, color)

        valid_moves = []
        for (to_row, to_col) in moves:
            if self._is_legal_move(row, col, to_row, to_col, color):
                valid_moves.append((to_row, to_col))
        return valid_moves

    def _is_legal_move(self, from_row, from_col, to_row, to_col, color):
        self.make_move(from_row, from_col, to_row, to_col)
        in_check = self.is_in_check(color)
        self.undo_move()
        return not in_check

    def _king_moves(self, row, col, color):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self._in_palace(new_row, new_col, color):
                target = self.board[new_row][new_col]
                if not target or self.get_piece_color(target) != color:
                    moves.append((new_row, new_col))
        moves.extend(self._flying_king_moves(row, col, color))
        return moves

    def _flying_king_moves(self, row, col, color):
        moves = []
        for r in range(BOARD_ROWS):
            target = self.board[r][col]
            if target and self.get_piece_type(target) == 'K' and self.get_piece_color(target) != color:
                blocked = False
                min_r, max_r = min(row, r), max(row, r)
                for rr in range(min_r + 1, max_r):
                    if self.board[rr][col]:
                        blocked = True
                        break
                if not blocked:
                    moves.append((r, col))
                break
        return moves

    def _in_palace(self, row, col, color):
        if col < 3 or col > 5:
            return False
        if color == RED:
            return 7 <= row <= 9
        else:
            return 0 <= row <= 2

    def _advisor_moves(self, row, col, color):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self._in_palace(new_row, new_col, color):
                target = self.board[new_row][new_col]
                if not target or self.get_piece_color(target) != color:
                    moves.append((new_row, new_col))
        return moves

    def _elephant_moves(self, row, col, color):
        moves = []
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        eye_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for i in range(4):
            dr, dc = directions[i]
            eye_dr, eye_dc = eye_offsets[i]
            new_row, new_col = row + dr, col + dc
            eye_row, eye_col = row + eye_dr, col + eye_dc
            if self.is_valid_position(new_row, new_col) and self._on_own_side(new_row, color):
                if not self.board[eye_row][eye_col]:
                    target = self.board[new_row][new_col]
                    if not target or self.get_piece_color(target) != color:
                        moves.append((new_row, new_col))
        return moves

    def _on_own_side(self, row, color):
        if color == RED:
            return row >= 5
        else:
            return row <= 4

    def _horse_moves(self, row, col, color):
        moves = []
        jumps = [
            (-2, -1, -1, 0), (-2, 1, -1, 0),
            (2, -1, 1, 0), (2, 1, 1, 0),
            (-1, -2, 0, -1), (1, -2, 0, -1),
            (-1, 2, 0, 1), (1, 2, 0, 1),
        ]
        for dr, dc, leg_dr, leg_dc in jumps:
            new_row, new_col = row + dr, col + dc
            leg_row, leg_col = row + leg_dr, col + leg_dc
            if self.is_valid_position(new_row, new_col):
                if not self.board[leg_row][leg_col]:
                    target = self.board[new_row][new_col]
                    if not target or self.get_piece_color(target) != color:
                        moves.append((new_row, new_col))
        return moves

    def _rook_moves(self, row, col, color):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.is_valid_position(r, c):
                target = self.board[r][c]
                if not target:
                    moves.append((r, c))
                else:
                    if self.get_piece_color(target) != color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves

    def _cannon_moves(self, row, col, color):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            jumped = False
            while self.is_valid_position(r, c):
                target = self.board[r][c]
                if not jumped:
                    if not target:
                        moves.append((r, c))
                    else:
                        jumped = True
                else:
                    if target:
                        if self.get_piece_color(target) != color:
                            moves.append((r, c))
                        break
                r += dr
                c += dc
        return moves

    def _pawn_moves(self, row, col, color):
        moves = []
        if color == RED:
            forward = -1
            crossed_river = row <= 4
        else:
            forward = 1
            crossed_river = row >= 5

        new_row = row + forward
        if self.is_valid_position(new_row, col):
            target = self.board[new_row][col]
            if not target or self.get_piece_color(target) != color:
                moves.append((new_row, col))

        if crossed_river:
            for dc in [-1, 1]:
                new_col = col + dc
                if self.is_valid_position(row, new_col):
                    target = self.board[row][new_col]
                    if not target or self.get_piece_color(target) != color:
                        moves.append((row, new_col))
        return moves

    def is_in_check(self, color):
        king_pos = self._find_king(color)
        if not king_pos:
            return True
        opponent = BLACK if color == RED else RED
        opponent_moves = self._get_all_capture_moves(opponent)
        return king_pos in opponent_moves

    def _find_king(self, color):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and self.get_piece_type(piece) == 'K' and self.get_piece_color(piece) == color:
                    return (row, col)
        return None

    def _get_all_capture_moves(self, color):
        positions = set()
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and self.get_piece_color(piece) == color:
                    moves = self._get_raw_moves(row, col)
                    for (r, c) in moves:
                        positions.add((r, c))
        return positions

    def _get_raw_moves(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return []
        piece_type = self.get_piece_type(piece)
        color = self.get_piece_color(piece)
        moves = []

        if piece_type == 'K':
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if self._in_palace(new_row, new_col, color):
                    target = self.board[new_row][new_col]
                    if not target or self.get_piece_color(target) != color:
                        moves.append((new_row, new_col))
        elif piece_type == 'A':
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if self._in_palace(new_row, new_col, color):
                    target = self.board[new_row][new_col]
                    if not target or self.get_piece_color(target) != color:
                        moves.append((new_row, new_col))
        elif piece_type == 'B':
            directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
            eye_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for i in range(4):
                dr, dc = directions[i]
                eye_dr, eye_dc = eye_offsets[i]
                new_row, new_col = row + dr, col + dc
                eye_row, eye_col = row + eye_dr, col + eye_dc
                if self.is_valid_position(new_row, new_col) and self._on_own_side(new_row, color):
                    if not self.board[eye_row][eye_col]:
                        target = self.board[new_row][new_col]
                        if not target or self.get_piece_color(target) != color:
                            moves.append((new_row, new_col))
        elif piece_type == 'N':
            jumps = [
                (-2, -1, -1, 0), (-2, 1, -1, 0),
                (2, -1, 1, 0), (2, 1, 1, 0),
                (-1, -2, 0, -1), (1, -2, 0, -1),
                (-1, 2, 0, 1), (1, 2, 0, 1),
            ]
            for dr, dc, leg_dr, leg_dc in jumps:
                new_row, new_col = row + dr, col + dc
                leg_row, leg_col = row + leg_dr, col + leg_dc
                if self.is_valid_position(new_row, new_col):
                    if not self.board[leg_row][leg_col]:
                        target = self.board[new_row][new_col]
                        if not target or self.get_piece_color(target) != color:
                            moves.append((new_row, new_col))
        elif piece_type == 'R':
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while self.is_valid_position(r, c):
                    target = self.board[r][c]
                    if not target:
                        moves.append((r, c))
                    else:
                        if self.get_piece_color(target) != color:
                            moves.append((r, c))
                        break
                    r += dr
                    c += dc
        elif piece_type == 'C':
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                jumped = False
                while self.is_valid_position(r, c):
                    target = self.board[r][c]
                    if not jumped:
                        if not target:
                            moves.append((r, c))
                        else:
                            jumped = True
                    else:
                        if target:
                            if self.get_piece_color(target) != color:
                                moves.append((r, c))
                            break
                    r += dr
                    c += dc
        elif piece_type == 'P':
            if color == RED:
                forward = -1
                crossed_river = row <= 4
            else:
                forward = 1
                crossed_river = row >= 5

            new_row = row + forward
            if self.is_valid_position(new_row, col):
                target = self.board[new_row][col]
                if not target or self.get_piece_color(target) != color:
                    moves.append((new_row, col))

            if crossed_river:
                for dc in [-1, 1]:
                    new_col = col + dc
                    if self.is_valid_position(row, new_col):
                        target = self.board[row][new_col]
                        if not target or self.get_piece_color(target) != color:
                            moves.append((row, new_col))
        return moves

    def is_game_over(self):
        red_moves = self.get_all_moves(RED)
        black_moves = self.get_all_moves(BLACK)
        return len(red_moves) == 0 or len(black_moves) == 0

    def get_winner(self):
        if not self.is_game_over():
            return None
        red_moves = self.get_all_moves(RED)
        if len(red_moves) == 0:
            return BLACK
        return RED

    def evaluate(self):
        score = 0
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece:
                    piece_type = self.get_piece_type(piece)
                    color = self.get_piece_color(piece)
                    value = PIECE_VALUES[piece_type]

                    if piece_type == 'P':
                        if color == RED:
                            value += PAWN_BONUS_RED[row][col]
                        else:
                            value += PAWN_BONUS_BLACK[row][col]

                    if color == RED:
                        score += value
                    else:
                        score -= value
        return score

    def display(self):
        print("  0 1 2 3 4 5 6 7 8")
        print("  -----------------")
        for row in range(BOARD_ROWS):
            line = f"{row}|"
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece:
                    name = PIECE_NAMES.get(piece, piece)
                    line += name
                else:
                    line += '·'
                line += ' '
            print(line)
        print(f"\n当前回合: {'红方' if self.current_player == RED else '黑方'}")
