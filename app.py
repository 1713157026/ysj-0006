from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from board import Board
from ai import ChessAI
from constants import RED, BLACK, PIECE_NAMES
import os

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

board = Board()
ai = ChessAI(depth=4)
game_mode = 'menu'
human_color = RED

def board_to_json():
    pieces = []
    for row in range(10):
        for col in range(9):
            piece = board.board[row][col]
            if piece:
                pieces.append({
                    'row': row,
                    'col': col,
                    'piece': piece,
                    'name': PIECE_NAMES.get(piece, piece),
                    'color': 'red' if piece[0] == 'r' else 'black'
                })
    return {
        'board': board.board,
        'pieces': pieces,
        'current_player': board.current_player,
        'current_player_name': '红方' if board.current_player == RED else '黑方',
        'is_game_over': board.is_game_over(),
        'winner': board.get_winner(),
        'winner_name': '红方' if board.get_winner() == RED else ('黑方' if board.get_winner() == BLACK else None),
        'red_in_check': board.is_in_check(RED),
        'black_in_check': board.is_in_check(BLACK),
        'evaluation': board.evaluate(),
        'game_mode': game_mode,
        'move_count': len(board.move_history)
    }

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/api/board', methods=['GET'])
def get_board():
    return jsonify(board_to_json())

@app.route('/api/moves', methods=['POST'])
def get_moves():
    data = request.json
    row = data.get('row')
    col = data.get('col')
    moves = board.get_piece_moves(row, col)
    return jsonify({'moves': moves})

@app.route('/api/move', methods=['POST'])
def make_move():
    global game_mode
    data = request.json
    from_row = data.get('from_row')
    from_col = data.get('from_col')
    to_row = data.get('to_row')
    to_col = data.get('to_col')
    
    piece = board.get_piece(from_row, from_col)
    valid_moves = board.get_piece_moves(from_row, from_col)
    
    if (to_row, to_col) not in valid_moves:
        return jsonify({'success': False, 'message': '无效的走法'})
    
    captured = board.make_move(from_row, from_col, to_row, to_col)
    captured_name = PIECE_NAMES.get(captured, '') if captured else ''
    piece_name = PIECE_NAMES.get(piece, piece)
    
    result = board_to_json()
    result['success'] = True
    result['message'] = f"{piece_name} {'吃 ' + captured_name if captured else '移动'}"
    result['captured'] = captured_name
    result['piece_moved'] = piece_name
    
    return jsonify(result)

@app.route('/api/ai/move', methods=['POST'])
def ai_move():
    global game_mode
    if board.is_game_over():
        return jsonify({'success': False, 'message': '游戏已结束'})
    
    best_move, score, nodes, elapsed = ai.find_best_move(board)
    
    if best_move is None:
        return jsonify({'success': False, 'message': 'AI无法找到有效走法'})
    
    from_r, from_c, to_r, to_c = best_move
    piece = board.get_piece(from_r, from_c)
    captured = board.get_piece(to_r, to_c)
    piece_name = PIECE_NAMES.get(piece, piece)
    captured_name = PIECE_NAMES.get(captured, '') if captured else ''
    
    board.make_move(from_r, from_c, to_r, to_c)
    
    result = board_to_json()
    result['success'] = True
    result['move'] = {
        'from': [from_r, from_c],
        'to': [to_r, to_c],
        'piece': piece_name,
        'captured': captured_name,
        'score': score,
        'nodes': nodes,
        'elapsed': elapsed
    }
    result['message'] = f"AI: {piece_name} {'吃 ' + captured_name if captured else '移动'}"
    
    return jsonify(result)

@app.route('/api/undo', methods=['POST'])
def undo_move():
    data = request.json
    steps = data.get('steps', 1)
    
    for _ in range(steps):
        if not board.undo_move():
            break
    
    return jsonify({
        'success': True,
        'message': '悔棋成功',
        **board_to_json()
    })

@app.route('/api/restart', methods=['POST'])
def restart():
    global board, game_mode
    board = Board()
    game_mode = 'menu'
    return jsonify({
        'success': True,
        'message': '已重新开始',
        **board_to_json()
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    steps = data.get('steps', 5)
    
    move_sequence, final_score = ai.predict_five_steps(board, steps)
    
    return jsonify({
        'success': True,
        'predictions': move_sequence,
        'final_score': final_score,
        'message': f'预测未来{len(move_sequence)}步'
    })

@app.route('/api/analyze', methods=['GET'])
def analyze():
    results = ai.analyze_position(board)
    
    return jsonify({
        'success': True,
        'analysis': results,
        'current_player': '红方' if board.current_player == RED else '黑方',
        'evaluation': board.evaluate(),
        'red_in_check': board.is_in_check(RED),
        'black_in_check': board.is_in_check(BLACK)
    })

@app.route('/api/mode', methods=['POST'])
def set_mode():
    global game_mode, human_color, board
    data = request.json
    mode = data.get('mode')
    color = data.get('color', 'red')
    
    game_mode = mode
    human_color = RED if color == 'red' else BLACK
    
    if mode == 'pvp':
        board = Board()
    
    return jsonify({
        'success': True,
        'mode': game_mode,
        'human_color': 'red' if human_color == RED else 'black',
        **board_to_json()
    })

@app.route('/api/rules', methods=['GET'])
def get_rules():
    rules = [
        {
            'name': '将/帅',
            'description': '只能在九宫格内移动，每次一格，横竖直走。双方将帅不能在同一直线上无遮挡对面（飞将规则）。',
            'value': 10000
        },
        {
            'name': '士/仕',
            'description': '只能在九宫格内斜走，每次一格。',
            'value': 20
        },
        {
            'name': '象/相',
            'description': '走田字，不能过河，田字中心（象眼）不能有棋子遮挡。',
            'value': 20
        },
        {
            'name': '马',
            'description': '走日字，前进方向前一格（马腿）不能有棋子遮挡。',
            'value': 40
        },
        {
            'name': '车',
            'description': '走直线，横竖直走，格数不限。',
            'value': 90
        },
        {
            'name': '炮',
            'description': '不吃子时走法同车；吃子时必须跳过一个棋子（炮台）。',
            'value': 45
        },
        {
            'name': '兵/卒',
            'description': '未过河只能向前走；过河后可向前、向左、向右走，每次一格。',
            'value': 10
        }
    ]
    
    return jsonify({
        'success': True,
        'rules': rules,
        'board_size': '10行 × 9列',
        'red_side': '下方（第7-9行）',
        'black_side': '上方（第0-2行）',
        'river': '楚河汉界在第4-5行之间'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"=" * 60)
    print(f"  中国象棋 Web UI 启动中...")
    print(f"  请在浏览器中访问: http://localhost:{port}")
    print(f"=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
