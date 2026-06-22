import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from board import Board
from ai import ChessAI
from constants import RED, BLACK, INITIAL_BOARD, PIECE_VALUES


def create_empty_board():
    """创建一个空棋盘，并放置双方的王在安全位置"""
    board = Board()
    board.board = [[''] * 9 for _ in range(10)]
    board.board[0][4] = 'bK'
    board.board[9][4] = 'rK'
    return board


class TestPieceMovements(unittest.TestCase):
    """测试各类棋子的移动规则"""

    def setUp(self):
        self.board = Board()

    def test_king_moves_in_palace(self):
        """测试将/帅只能在九宫格内移动"""
        board = create_empty_board()
        board.current_player = BLACK

        moves = board.get_piece_moves(0, 4)
        self.assertGreaterEqual(len(moves), 3)
        self.assertIn((1, 4), moves)
        self.assertIn((0, 3), moves)
        self.assertIn((0, 5), moves)
        self.assertNotIn((0, 2), moves)
        self.assertNotIn((3, 4), moves)

    def test_king_cannot_leave_palace(self):
        """测试将/帅不能离开九宫格"""
        board = create_empty_board()
        board.board[2][4] = 'bK'
        board.board[0][4] = ''
        board.current_player = BLACK

        moves = board.get_piece_moves(2, 4)
        self.assertNotIn((3, 4), moves)

    def test_advisor_moves_diagonally(self):
        """测试士/仕只能斜走一步且在九宫格内"""
        board = create_empty_board()
        board.board[0][3] = 'bA'
        board.current_player = BLACK

        moves = board.get_piece_moves(0, 3)
        self.assertEqual(len(moves), 1)
        self.assertIn((1, 4), moves)

    def test_elephant_crosses_river(self):
        """测试象/相不能过河（红相不能走到第4行及以上）"""
        board = create_empty_board()
        board.board[7][4] = 'rB'
        board.current_player = RED

        moves = board.get_piece_moves(7, 4)
        self.assertIn((9, 2), moves)
        self.assertIn((9, 6), moves)
        self.assertIn((5, 2), moves)
        self.assertIn((5, 6), moves)

        board.board[5][4] = 'rB'
        board.board[7][4] = ''
        moves = board.get_piece_moves(5, 4)
        self.assertNotIn((3, 2), moves)
        self.assertNotIn((3, 6), moves)

    def test_elephant_blocked_eye(self):
        """测试象眼被塞时不能移动"""
        board = create_empty_board()
        board.board[0][2] = 'bB'
        board.board[1][3] = 'bP'
        board.current_player = BLACK

        moves = board.get_piece_moves(0, 2)
        self.assertNotIn((2, 4), moves)

    def test_elephant_valid_moves(self):
        """测试象的有效走法（角落的象只有一步）"""
        board = create_empty_board()
        board.board[0][0] = 'bB'
        board.current_player = BLACK

        moves = board.get_piece_moves(0, 0)
        self.assertEqual(len(moves), 1)
        self.assertIn((2, 2), moves)

    def test_horse_moves_l_shape(self):
        """测试马走日字"""
        board = create_empty_board()
        board.board[4][4] = 'rN'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertEqual(len(moves), 8)

    def test_horse_blocked_leg(self):
        """测试马腿被绊时不能移动"""
        board = create_empty_board()
        board.board[4][4] = 'rN'
        board.board[3][4] = 'rP'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertNotIn((2, 3), moves)
        self.assertNotIn((2, 5), moves)
        self.assertIn((6, 3), moves)
        self.assertIn((6, 5), moves)

    def test_rook_moves_straight(self):
        """测试车走直线（在空棋盘中间应有17步）"""
        board = Board()
        board.board = [[''] * 9 for _ in range(10)]
        board.board[4][4] = 'rR'
        board.board[0][0] = 'bK'
        board.board[9][8] = 'rK'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertEqual(len(moves), 17)

    def test_rook_blocked_by_piece(self):
        """测试车被棋子阻挡"""
        board = create_empty_board()
        board.board[4][4] = 'rR'
        board.board[4][6] = 'rP'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertNotIn((4, 7), moves)
        self.assertNotIn((4, 6), moves)
        self.assertIn((4, 5), moves)

    def test_rook_captures_enemy(self):
        """测试车可以吃敌方棋子"""
        board = create_empty_board()
        board.board[4][4] = 'rR'
        board.board[4][6] = 'bP'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertIn((4, 6), moves)
        self.assertNotIn((4, 7), moves)

    def test_cannon_moves_without_capture(self):
        """测试炮不吃子时走法同车"""
        board = Board()
        board.board = [[''] * 9 for _ in range(10)]
        board.board[4][4] = 'rC'
        board.board[0][0] = 'bK'
        board.board[9][8] = 'rK'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertEqual(len(moves), 17)

    def test_cannon_cannot_capture_directly(self):
        """测试炮不能直接吃子"""
        board = create_empty_board()
        board.board[4][4] = 'rC'
        board.board[4][6] = 'bP'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertNotIn((4, 6), moves)

    def test_cannon_captures_over_piece(self):
        """测试炮必须隔子吃子"""
        board = create_empty_board()
        board.board[4][4] = 'rC'
        board.board[4][6] = 'bP'
        board.board[4][5] = 'rP'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertIn((4, 6), moves)

    def test_pawn_moves_forward(self):
        """测试兵/卒未过河时只能向前"""
        board = create_empty_board()
        board.board[6][4] = 'rP'
        board.current_player = RED

        moves = board.get_piece_moves(6, 4)
        self.assertEqual(len(moves), 1)
        self.assertIn((5, 4), moves)

    def test_pawn_cannot_move_backward(self):
        """测试兵/卒不能后退"""
        board = create_empty_board()
        board.board[6][4] = 'rP'
        board.current_player = RED

        moves = board.get_piece_moves(6, 4)
        self.assertNotIn((7, 4), moves)

    def test_pawn_crossed_river_moves_sideways(self):
        """测试兵/卒过河后可以左右移动"""
        board = create_empty_board()
        board.board[4][4] = 'rP'
        board.current_player = RED

        moves = board.get_piece_moves(4, 4)
        self.assertEqual(len(moves), 3)
        self.assertIn((3, 4), moves)
        self.assertIn((4, 3), moves)
        self.assertIn((4, 5), moves)

    def test_black_pawn_moves_forward(self):
        """测试黑方卒的移动方向"""
        board = create_empty_board()
        board.board[3][4] = 'bP'
        board.current_player = BLACK

        moves = board.get_piece_moves(3, 4)
        self.assertEqual(len(moves), 1)
        self.assertIn((4, 4), moves)


class TestCheckAndCheckmate(unittest.TestCase):
    """测试将军与将死"""

    def test_initial_board_not_in_check(self):
        """初始局面不应被将军"""
        board = Board()
        self.assertFalse(board.is_in_check(RED))
        self.assertFalse(board.is_in_check(BLACK))

    def test_simple_check(self):
        """测试简单的将军局面"""
        board = create_empty_board()
        board.board[3][4] = 'rR'
        board.current_player = BLACK

        self.assertTrue(board.is_in_check(BLACK))

    def test_check_can_be_blocked(self):
        """测试将军可以被阻挡"""
        board = create_empty_board()
        board.board[3][4] = 'rR'
        board.board[1][4] = 'bA'
        board.current_player = BLACK

        self.assertFalse(board.is_in_check(BLACK))

    def test_checkmate(self):
        """测试将死局面"""
        board = create_empty_board()
        board.board[0][3] = 'bA'
        board.board[0][5] = 'bA'
        board.board[1][4] = 'bA'
        board.board[2][4] = 'rR'
        board.board[1][3] = 'rR'
        board.current_player = BLACK

        moves = board.get_all_moves(BLACK)
        self.assertEqual(len(moves), 0)
        self.assertTrue(board.is_game_over())
        self.assertEqual(board.get_winner(), RED)

    def test_flying_king(self):
        """测试飞将规则"""
        board = create_empty_board()
        board.current_player = RED

        moves = board.get_piece_moves(9, 4)
        self.assertIn((0, 4), moves)

    def test_flying_king_blocked(self):
        """测试飞将被阻挡时无效"""
        board = create_empty_board()
        board.board[5][4] = 'rP'
        board.current_player = RED

        moves = board.get_piece_moves(9, 4)
        self.assertNotIn((0, 4), moves)

    def test_must_get_out_of_check(self):
        """测试被将军时必须应将"""
        board = create_empty_board()
        board.board[2][4] = 'rR'
        board.current_player = BLACK

        moves = board.get_all_moves(BLACK)
        for move in moves:
            from_r, from_c, to_r, to_c = move
            board.make_move(from_r, from_c, to_r, to_c)
            self.assertFalse(board.is_in_check(BLACK))
            board.undo_move()


class TestBoardOperations(unittest.TestCase):
    """测试棋盘操作"""

    def test_initial_board_setup(self):
        """测试初始棋盘设置"""
        board = Board()
        self.assertEqual(board.board[0][0], 'bR')
        self.assertEqual(board.board[0][4], 'bK')
        self.assertEqual(board.board[9][4], 'rK')
        self.assertEqual(board.board[2][1], 'bC')
        self.assertEqual(board.board[7][1], 'rC')

    def test_make_and_undo_move(self):
        """测试走棋和悔棋"""
        board = Board()
        initial_state = [row[:] for row in board.board]
        initial_player = board.current_player
        history_len = len(board.move_history)

        board.make_move(7, 1, 2, 1)
        self.assertNotEqual(board.board, initial_state)
        self.assertEqual(len(board.move_history), history_len + 1)

        board.undo_move()
        self.assertEqual(board.board, initial_state)
        self.assertEqual(board.current_player, initial_player)
        self.assertEqual(len(board.move_history), history_len)

    def test_capture_piece(self):
        """测试吃子（车吃兵）"""
        board = create_empty_board()
        board.board[5][4] = 'bP'
        board.board[7][4] = 'rR'
        board.current_player = RED

        captured = board.make_move(7, 4, 5, 4)
        self.assertEqual(captured, 'bP')

    def test_current_player_switches(self):
        """测试走棋后当前玩家切换"""
        board = Board()
        self.assertEqual(board.current_player, RED)
        board.make_move(7, 1, 6, 1)
        self.assertEqual(board.current_player, BLACK)
        board.make_move(2, 1, 3, 1)
        self.assertEqual(board.current_player, RED)


class TestEvaluation(unittest.TestCase):
    """测试评估函数"""

    def test_initial_evaluation(self):
        """初始局面评估应为0（双方子力相等）"""
        board = Board()
        score = board.evaluate()
        self.assertEqual(score, 0)

    def test_red_advantage(self):
        """红方多子时评估应为正"""
        board = Board()
        board.board[0][0] = ''
        score = board.evaluate()
        self.assertGreater(score, 0)

    def test_black_advantage(self):
        """黑方多子时评估应为负"""
        board = Board()
        board.board[9][0] = ''
        score = board.evaluate()
        self.assertLess(score, 0)

    def test_king_value_highest(self):
        """将/帅的价值最高"""
        self.assertGreater(PIECE_VALUES['K'], PIECE_VALUES['R'])
        self.assertGreater(PIECE_VALUES['R'], PIECE_VALUES['C'])
        self.assertGreater(PIECE_VALUES['C'], PIECE_VALUES['N'])

    def test_pawn_position_bonus(self):
        """过河兵有额外加分"""
        board1 = create_empty_board()
        board1.board[6][4] = 'rP'
        score1 = board1.evaluate()

        board2 = create_empty_board()
        board2.board[3][4] = 'rP'
        score2 = board2.evaluate()

        self.assertGreater(score2, score1)


class TestAI(unittest.TestCase):
    """测试AI搜索算法"""

    def setUp(self):
        self.ai = ChessAI(depth=3)
        self.board = Board()

    def test_ai_returns_valid_move(self):
        """AI应返回有效的走法"""
        best_move, score, nodes, elapsed = self.ai.find_best_move(self.board)
        self.assertIsNotNone(best_move)
        self.assertEqual(len(best_move), 4)

        from_r, from_c, to_r, to_c = best_move
        piece = self.board.get_piece(from_r, from_c)
        self.assertIsNotNone(piece)
        self.assertEqual(self.board.get_piece_color(piece), RED)

        valid_moves = self.board.get_piece_moves(from_r, from_c)
        self.assertIn((to_r, to_c), valid_moves)

    def test_ai_captures_when_possible(self):
        """AI在有子可吃时应该吃子（吃有价值的子）"""
        board = create_empty_board()
        board.board[5][4] = 'bR'
        board.board[4][4] = 'rR'
        board.current_player = RED

        ai = ChessAI(depth=3)
        best_move, score, _, _ = ai.find_best_move(board)
        from_r, from_c, to_r, to_c = best_move

        captured = board.board[to_r][to_c]
        self.assertIsNotNone(captured)
        self.assertEqual(captured, 'bR')

    def test_ai_protects_king(self):
        """AI应避免被将死"""
        board = create_empty_board()
        board.board[0][3] = 'bA'
        board.board[0][5] = 'bA'
        board.board[2][4] = 'rR'
        board.board[2][3] = 'rC'
        board.current_player = BLACK

        ai = ChessAI(depth=3)
        best_move, score, _, _ = ai.find_best_move(board)

        if best_move:
            board.make_move(best_move[0], best_move[1], best_move[2], best_move[3])
            self.assertFalse(board.is_in_check(BLACK))

    def test_minimax_consistency(self):
        """测试同一局面多次搜索结果一致"""
        board = Board()
        ai = ChessAI(depth=2)

        move1, score1, _, _ = ai.find_best_move(board)
        move2, score2, _, _ = ai.find_best_move(board)

        self.assertEqual(move1, move2)
        self.assertEqual(score1, score2)

    def test_ai_black_plays(self):
        """测试黑方AI也能正常走棋"""
        board = Board()
        board.current_player = BLACK

        ai = ChessAI(depth=2)
        best_move, score, _, _ = ai.find_best_move(board)

        self.assertIsNotNone(best_move)
        from_r, from_c, to_r, to_c = best_move
        piece = board.get_piece(from_r, from_c)
        self.assertEqual(board.get_piece_color(piece), BLACK)


class TestFiveStepPrediction(unittest.TestCase):
    """测试五步预测功能"""

    def test_prediction_returns_steps(self):
        """预测应返回最多五步"""
        board = Board()
        ai = ChessAI(depth=3)

        move_sequence, final_score = ai.predict_five_steps(board)

        self.assertIsInstance(move_sequence, list)
        self.assertLessEqual(len(move_sequence), 5)
        self.assertGreater(len(move_sequence), 0)

    def test_prediction_steps_are_valid(self):
        """预测的每一步都应该是有效的"""
        board = Board()
        ai = ChessAI(depth=2)

        move_sequence, final_score = ai.predict_five_steps(board)

        temp_board = Board(board.board)
        temp_board.current_player = board.current_player

        for step in move_sequence:
            from_r, from_c = step['from']
            to_r, to_c = step['to']

            piece = temp_board.get_piece(from_r, from_c)
            self.assertIsNotNone(piece)

            valid_moves = temp_board.get_piece_moves(from_r, from_c)
            self.assertIn((to_r, to_c), valid_moves)

            temp_board.make_move(from_r, from_c, to_r, to_c)

    def test_prediction_alternates_players(self):
        """预测的走法应该轮流由红黑双方执行"""
        board = Board()
        ai = ChessAI(depth=2)

        move_sequence, _ = ai.predict_five_steps(board)

        if len(move_sequence) >= 2:
            first_player = move_sequence[0]['player']
            second_player = move_sequence[1]['player']
            self.assertNotEqual(first_player, second_player)

    def test_prediction_has_piece_info(self):
        """预测结果应包含棋子名称信息"""
        board = Board()
        ai = ChessAI(depth=2)

        move_sequence, _ = ai.predict_five_steps(board)

        for step in move_sequence:
            self.assertIn('piece', step)
            self.assertIn('player', step)
            self.assertIn('from', step)
            self.assertIn('to', step)
            self.assertIsInstance(step['from'], tuple)
            self.assertIsInstance(step['to'], tuple)


class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_depth_2_completes_quickly(self):
        """深度2搜索应快速完成"""
        import time
        board = Board()
        ai = ChessAI(depth=2)

        start = time.time()
        ai.find_best_move(board)
        elapsed = time.time() - start

        self.assertLess(elapsed, 10)

    def test_alpha_beta_pruning_effectiveness(self):
        """Alpha-Beta剪枝应减少搜索节点数"""
        board = Board()
        ai = ChessAI(depth=3)

        _, _, nodes, _ = ai.find_best_move(board)

        max_possible = 40 ** 3
        self.assertLess(nodes, max_possible)

    def test_nodes_count_positive(self):
        """搜索节点数应为正"""
        board = Board()
        ai = ChessAI(depth=2)

        _, _, nodes, _ = ai.find_best_move(board)
        self.assertGreater(nodes, 0)


class TestEndgame(unittest.TestCase):
    """残局测试"""

    def test_rook_vs_single_king(self):
        """车对单将的残局，红方应占优"""
        board = create_empty_board()
        board.board[5][0] = 'rR'
        board.current_player = RED

        ai = ChessAI(depth=3)
        best_move, score, _, _ = ai.find_best_move(board)

        self.assertIsNotNone(best_move)
        self.assertGreater(score, 0)

    def test_two_rooks_vs_king(self):
        """双车对将，优势明显"""
        board = create_empty_board()
        board.board[2][0] = 'rR'
        board.board[2][8] = 'rR'
        board.current_player = RED

        score = board.evaluate()
        self.assertGreater(score, 100)

    def test_endgame_evaluation(self):
        """残局评估正确性"""
        board = create_empty_board()
        score_even = board.evaluate()

        board.board[5][0] = 'rR'
        score_red_up = board.evaluate()

        self.assertGreater(score_red_up, score_even)


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("  中国象棋预测程序 - 验证测试")
    print("=" * 60)

    test_cases = [
        ("棋子移动规则测试", TestPieceMovements),
        ("将军与将死测试", TestCheckAndCheckmate),
        ("棋盘操作测试", TestBoardOperations),
        ("评估函数测试", TestEvaluation),
        ("AI搜索算法测试", TestAI),
        ("五步预测功能测试", TestFiveStepPrediction),
        ("性能测试", TestPerformance),
        ("残局测试", TestEndgame),
    ]

    total_tests = 0
    total_passed = 0
    total_failed = 0

    for name, test_class in test_cases:
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")

        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        total_tests += result.testsRun
        total_passed += result.testsRun - len(result.failures) - len(result.errors)
        total_failed += len(result.failures) + len(result.errors)

    print(f"\n{'='*60}")
    print(f"  测试汇总")
    print(f"{'='*60}")
    print(f"  总测试数: {total_tests}")
    print(f"  通过: {total_passed}")
    print(f"  失败: {total_failed}")
    if total_tests > 0:
        print(f"  通过率: {total_passed/total_tests*100:.1f}%")
    print(f"{'='*60}")

    return total_failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
