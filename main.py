from board import Board
from ai import ChessAI
from constants import RED, BLACK, PIECE_NAMES
import sys


def print_menu():
    print("\n" + "=" * 50)
    print("       中国象棋预测程序")
    print("=" * 50)
    print("1. 人机对战")
    print("2. 预测未来五步")
    print("3. 分析当前局面")
    print("4. 查看棋盘")
    print("5. 输入走法")
    print("6. 悔棋")
    print("7. 重新开始")
    print("0. 退出")
    print("=" * 50)


def human_move(board):
    print("\n请输入走法 (格式: 起始行 起始列 目标行 目标列)")
    print("例如: 7 1 2 1  表示 七路炮 前进到 第二行")
    print("输入 'q' 返回主菜单")

    while True:
        try:
            user_input = input("请输入: ").strip()
            if user_input.lower() == 'q':
                return False

            parts = user_input.split()
            if len(parts) != 4:
                print("输入格式错误，请输入四个数字")
                continue

            from_r, from_c, to_r, to_c = map(int, parts)

            if not board.is_valid_position(from_r, from_c) or not board.is_valid_position(to_r, to_c):
                print("位置超出棋盘范围")
                continue

            piece = board.get_piece(from_r, from_c)
            if not piece:
                print("起始位置没有棋子")
                continue

            if board.get_piece_color(piece) != board.current_player:
                print("不是你的棋子")
                continue

            valid_moves = board.get_piece_moves(from_r, from_c)
            if (to_r, to_c) not in valid_moves:
                print("无效的走法")
                continue

            captured = board.make_move(from_r, from_c, to_r, to_c)
            captured_name = PIECE_NAMES.get(captured, '') if captured else ''
            piece_name = PIECE_NAMES.get(piece, piece)

            if captured:
                print(f"{piece_name} 吃 {captured_name}")
            else:
                print(f"{piece_name} 移动")

            return True

        except ValueError:
            print("输入格式错误，请输入数字")


def ai_move(board, ai):
    print(f"\nAI 思考中 (搜索深度: {ai.depth} 步)...")
    best_move, score, nodes, elapsed = ai.find_best_move(board)

    if best_move is None:
        print("AI 无法找到有效走法！")
        return False

    from_r, from_c, to_r, to_c = best_move
    piece = board.get_piece(from_r, from_c)
    captured = board.get_piece(to_r, to_c)
    piece_name = PIECE_NAMES.get(piece, piece)
    captured_name = PIECE_NAMES.get(captured, '') if captured else ''

    board.make_move(from_r, from_c, to_r, to_c)

    print(f"AI 走法: {piece_name} ({from_r},{from_c}) -> ({to_r},{to_c})")
    if captured:
        print(f"吃掉: {captured_name}")
    print(f"评估分数: {score}")
    print(f"搜索节点: {nodes}")
    print(f"耗时: {elapsed:.2f} 秒")
    return True


def predict_five_steps(board, ai):
    print("\n" + "=" * 50)
    print("       预测未来五步")
    print("=" * 50)

    print("正在分析未来五步的最佳走法...")
    move_sequence, final_score = ai.predict_five_steps(board)

    if not move_sequence:
        print("无法预测有效走法")
        return

    print(f"\n预测的走法序列 (共 {len(move_sequence)} 步):")
    print("-" * 50)

    for i, step in enumerate(move_sequence, 1):
        from_r, from_c = step['from']
        to_r, to_c = step['to']
        piece = step['piece']
        captured = step['captured']
        player = step['player']

        if captured:
            print(f"第 {i} 步 ({player}): {piece} ({from_r},{from_c}) -> ({to_r},{to_c}) 吃 {captured}")
        else:
            print(f"第 {i} 步 ({player}): {piece} ({from_r},{from_c}) -> ({to_r},{to_c})")

    print("-" * 50)
    print(f"预测最终局面评估分: {final_score}")
    print("  (正数表示红方占优，负数表示黑方占优)")

    print("\n是否在棋盘上模拟这五步？(y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        temp_board = Board(board.board)
        temp_board.current_player = board.current_player
        print("\n模拟走法:")
        for i, step in enumerate(move_sequence, 1):
            from_r, from_c = step['from']
            to_r, to_c = step['to']
            temp_board.make_move(from_r, from_c, to_r, to_c)
            print(f"\n--- 第 {i} 步后 ---")
            temp_board.display()


def analyze_position(board, ai):
    print("\n" + "=" * 50)
    print("       局面分析")
    print("=" * 50)

    print(f"当前回合: {'红方' if board.current_player == RED else '黑方'}")
    print(f"局面评估分: {board.evaluate()}")
    print(f"红方是否被将军: {'是' if board.is_in_check(RED) else '否'}")
    print(f"黑方是否被将军: {'是' if board.is_in_check(BLACK) else '否'}")

    print(f"\nAI 分析中 (深度: {ai.depth})...")
    results = ai.analyze_position(board)

    print(f"\n最佳走法候选 (前10):")
    print("-" * 60)
    print(f"{'序号':<4} {'棋子':<4} {'走法':<14} {'吃子':<4} {'评分':<8}")
    print("-" * 60)

    for i, result in enumerate(results, 1):
        from_r, from_c = result['from']
        to_r, to_c = result['to']
        move_str = f"({from_r},{from_c})->({to_r},{to_c})"
        print(f"{i:<4} {result['piece']:<4} {move_str:<14} {result['captured']:<4} {result['score']:<8}")


def game_loop():
    board = Board()
    ai = ChessAI(depth=5)

    print("欢迎使用中国象棋预测程序！")
    print("默认搜索深度: 5 步")

    while True:
        print_menu()
        choice = input("请选择 (0-7): ").strip()

        if choice == '0':
            print("再见！")
            break

        elif choice == '1':
            print("\n人机对战模式")
            print("你执红棋(下方)，AI执黑棋(上方)")

            human_color = RED
            ai_color = BLACK

            while not board.is_game_over():
                board.display()

                if board.current_player == human_color:
                    if not human_move(board):
                        break
                else:
                    if not ai_move(board, ai):
                        break

                if board.is_in_check(board.current_player):
                    print(f"{'红方' if board.current_player == RED else '黑方'} 被将军！")

            board.display()
            winner = board.get_winner()
            if winner:
                print(f"\n游戏结束！{'红方' if winner == RED else '黑方'} 获胜！")
            else:
                print("\n游戏结束！")

        elif choice == '2':
            predict_five_steps(board, ai)

        elif choice == '3':
            analyze_position(board, ai)

        elif choice == '4':
            board.display()
            if board.is_in_check(RED):
                print("红方被将军！")
            if board.is_in_check(BLACK):
                print("黑方被将军！")

        elif choice == '5':
            board.display()
            human_move(board)

        elif choice == '6':
            if board.undo_move():
                print("悔棋成功")
            else:
                print("无法悔棋")

        elif choice == '7':
            board = Board()
            print("已重新开始")

        else:
            print("无效的选择，请重新输入")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("运行测试模式...")
        return

    game_loop()


if __name__ == '__main__':
    main()
