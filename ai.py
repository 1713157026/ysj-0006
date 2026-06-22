from board import Board
from constants import RED, BLACK, PIECE_VALUES
import time


class ChessAI:
    def __init__(self, depth=5):
        self.depth = depth
        self.nodes_visited = 0
        self.transposition_table = {}

    def find_best_move(self, board):
        self.nodes_visited = 0
        start_time = time.time()
        color = board.current_player
        best_move = None
        best_score = float('-inf') if color == RED else float('inf')

        moves = self._order_moves(board, board.get_all_moves(color))

        alpha = float('-inf')
        beta = float('inf')

        for move in moves:
            from_r, from_c, to_r, to_c = move
            captured = board.make_move(from_r, from_c, to_r, to_c)
            score = self._minimax(board, self.depth - 1, alpha, beta, False if color == RED else True)
            board.undo_move()

            if color == RED:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, best_score)

        elapsed = time.time() - start_time
        return best_move, best_score, self.nodes_visited, elapsed

    def predict_five_steps(self, board, steps=5):
        """
        预测未来几步的走法序列
        返回: (move_sequence, final_score)
            move_sequence: 列表，每个元素是字典，包含 from, to, piece, captured, player
            final_score: 最终局面评估分数
        """
        pv = []
        temp_board = Board(board.board)
        temp_board.current_player = board.current_player
        final_score = 0

        for i in range(steps):
            color = temp_board.current_player
            moves = temp_board.get_all_moves(color)
            if not moves:
                break

            best_move = None
            best_score = float('-inf') if color == RED else float('inf')

            ordered_moves = self._order_moves(temp_board, moves)
            search_depth = max(1, self.depth - 1)

            for move in ordered_moves:
                from_r, from_c, to_r, to_c = move
                captured = temp_board.make_move(from_r, from_c, to_r, to_c)
                score = self._minimax(temp_board, search_depth - 1, float('-inf'), float('inf'),
                                     False if color == RED else True)
                temp_board.undo_move()

                if color == RED:
                    if score > best_score:
                        best_score = score
                        best_move = move
                else:
                    if score < best_score:
                        best_score = score
                        best_move = move

            if best_move is None:
                break

            from_r, from_c, to_r, to_c = best_move
            piece = temp_board.board[from_r][from_c]
            captured = temp_board.board[to_r][to_c]

            from constants import PIECE_NAMES
            piece_name = PIECE_NAMES.get(piece, piece)
            captured_name = PIECE_NAMES.get(captured, '') if captured else ''

            pv.append({
                'from': (from_r, from_c),
                'to': (to_r, to_c),
                'piece': piece_name,
                'captured': captured_name,
                'player': '红方' if color == RED else '黑方'
            })

            temp_board.make_move(from_r, from_c, to_r, to_c)
            final_score = best_score

        return pv, final_score

    def _minimax(self, board, depth, alpha, beta, maximizing):
        self.nodes_visited += 1

        if depth == 0 or board.is_game_over():
            return board.evaluate()

        color = RED if maximizing else BLACK
        moves = board.get_all_moves(color)

        if not moves:
            return board.evaluate()

        moves = self._order_moves(board, moves)

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                from_r, from_c, to_r, to_c = move
                captured = board.make_move(from_r, from_c, to_r, to_c)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                board.undo_move()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                from_r, from_c, to_r, to_c = move
                captured = board.make_move(from_r, from_c, to_r, to_c)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                board.undo_move()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _order_moves(self, board, moves):
        """
        移动排序，提高 Alpha-Beta 剪枝效率
        吃子优先，价值大的棋子优先
        """
        scored_moves = []
        for move in moves:
            from_r, from_c, to_r, to_c = move
            captured = board.board[to_r][to_c]
            score = 0

            if captured:
                captured_type = captured[1]
                moving_piece = board.board[from_r][from_c]
                moving_type = moving_piece[1]
                score += PIECE_VALUES[captured_type] * 10 - PIECE_VALUES[moving_type]

            scored_moves.append((score, move))

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [move for _, move in scored_moves]

    def analyze_position(self, board):
        """
        分析当前局面，返回多个候选走法及其评分
        """
        color = board.current_player
        moves = board.get_all_moves(color)
        results = []

        ordered_moves = self._order_moves(board, moves)[:10]

        for move in ordered_moves:
            from_r, from_c, to_r, to_c = move
            captured = board.make_move(from_r, from_c, to_r, to_c)
            score = self._minimax(board, self.depth - 1, float('-inf'), float('inf'),
                                 False if color == RED else True)
            board.undo_move()

            from constants import PIECE_NAMES
            piece = board.board[from_r][from_c]
            piece_name = PIECE_NAMES.get(piece, piece)
            captured_piece = board.board[to_r][to_c]
            captured_name = PIECE_NAMES.get(captured_piece, '') if captured_piece else ''

            results.append({
                'move': (from_r, from_c, to_r, to_c),
                'piece': piece_name,
                'captured': captured_name,
                'score': score,
                'from': (from_r, from_c),
                'to': (to_r, to_c)
            })

        results.sort(key=lambda x: x['score'], reverse=(color == RED))
        return results
