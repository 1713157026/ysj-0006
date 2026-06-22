const API_BASE = '/api';

const state = {
    board: null,
    selectedPiece: null,
    validMoves: [],
    gameMode: 'menu',
    humanColor: 'red',
    isAIThinking: false,
    lastMove: null,
    capturedPieces: {
        red: [],
        black: []
    }
};

const elements = {
    piecesContainer: document.getElementById('pieces-container'),
    validMovesContainer: document.getElementById('valid-moves-container'),
    lastMoveIndicator: document.getElementById('last-move-indicator'),
    currentPlayer: document.getElementById('current-player'),
    moveCount: document.getElementById('move-count'),
    evaluation: document.getElementById('evaluation'),
    checkStatus: document.getElementById('check-status'),
    messages: document.getElementById('messages'),
    redCaptured: document.getElementById('red-captured'),
    blackCaptured: document.getElementById('black-captured'),
    modalOverlay: document.getElementById('modal-overlay'),
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    modalFooter: document.getElementById('modal-footer'),
    modalClose: document.getElementById('modal-close'),
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingText: document.getElementById('loading-text')
};

const CELL_SIZE = 60;
const BOARD_OFFSET_X = 30;
const BOARD_OFFSET_Y = 30;

function gridToPixel(row, col) {
    return {
        x: BOARD_OFFSET_X + col * CELL_SIZE,
        y: BOARD_OFFSET_Y + row * CELL_SIZE
    };
}

function pixelToGrid(x, y) {
    return {
        row: Math.round((y - BOARD_OFFSET_Y) / CELL_SIZE),
        col: Math.round((x - BOARD_OFFSET_X) / CELL_SIZE)
    };
}

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    return await response.json();
}

function showLoading(text = '加载中...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function addMessage(text, type = 'info') {
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    elements.messages.insertBefore(message, elements.messages.firstChild);
    
    while (elements.messages.children.length > 20) {
        elements.messages.removeChild(elements.messages.lastChild);
    }
}

function showModal(title, bodyContent, footerContent = null) {
    elements.modalTitle.textContent = title;
    elements.modalBody.innerHTML = bodyContent;
    elements.modalFooter.innerHTML = footerContent || '';
    elements.modalOverlay.style.display = 'flex';
}

function hideModal() {
    elements.modalOverlay.style.display = 'none';
}

function renderBoard() {
    elements.piecesContainer.innerHTML = '';
    elements.validMovesContainer.innerHTML = '';
    elements.lastMoveIndicator.innerHTML = '';

    if (!state.board) return;

    state.board.pieces.forEach(piece => {
        const { x, y } = gridToPixel(piece.row, piece.col);
        const pieceEl = document.createElement('div');
        pieceEl.className = `piece ${piece.color}`;
        pieceEl.textContent = piece.name;
        pieceEl.style.left = `${x - 25}px`;
        pieceEl.style.top = `${y - 25}px`;
        pieceEl.dataset.row = piece.row;
        pieceEl.dataset.col = piece.col;
        pieceEl.dataset.piece = piece.piece;

        if (state.selectedPiece && 
            state.selectedPiece.row === piece.row && 
            state.selectedPiece.col === piece.col) {
            pieceEl.classList.add('selected');
        }

        pieceEl.addEventListener('click', (e) => handlePieceClick(piece, e));
        elements.piecesContainer.appendChild(pieceEl);
    });

    if (state.lastMove) {
        const fromPos = gridToPixel(state.lastMove.from[0], state.lastMove.from[1]);
        const toPos = gridToPixel(state.lastMove.to[0], state.lastMove.to[1]);
        
        const fromCell = document.createElement('div');
        fromCell.className = 'last-move-cell';
        fromCell.style.left = `${fromPos.x}px`;
        fromCell.style.top = `${fromPos.y}px`;
        elements.lastMoveIndicator.appendChild(fromCell);
        
        const toCell = document.createElement('div');
        toCell.className = 'last-move-cell';
        toCell.style.left = `${toPos.x}px`;
        toCell.style.top = `${toPos.y}px`;
        elements.lastMoveIndicator.appendChild(toCell);
    }
}

function renderValidMoves() {
    elements.validMovesContainer.innerHTML = '';

    state.validMoves.forEach(move => {
        const { x, y } = gridToPixel(move[0], move[1]);
        const moveEl = document.createElement('div');
        
        const targetPiece = state.board.board[move[0]][move[1]];
        moveEl.className = `valid-move ${targetPiece ? 'capture' : ''}`;
        moveEl.style.left = `${x}px`;
        moveEl.style.top = `${y}px`;
        
        moveEl.addEventListener('click', (e) => {
            e.stopPropagation();
            handleMoveClick(move[0], move[1]);
        });
        
        elements.validMovesContainer.appendChild(moveEl);
    });
}

function updateGameInfo() {
    if (!state.board) return;

    elements.currentPlayer.textContent = state.board.current_player_name;
    elements.moveCount.textContent = state.board.move_count;
    elements.evaluation.textContent = state.board.evaluation;

    const inCheck = state.board.current_player === 'red' 
        ? state.board.red_in_check 
        : state.board.black_in_check;

    if (inCheck) {
        elements.checkStatus.textContent = `${state.board.current_player_name} 被将军！`;
        elements.checkStatus.classList.add('active');
    } else if (state.board.red_in_check || state.board.black_in_check) {
        const checkedPlayer = state.board.red_in_check ? '红方' : '黑方';
        elements.checkStatus.textContent = `${checkedPlayer} 被将军！`;
        elements.checkStatus.classList.add('active');
    } else {
        elements.checkStatus.classList.remove('active');
    }
}

function updateCapturedPieces() {
    elements.redCaptured.innerHTML = '';
    elements.blackCaptured.innerHTML = '';

    state.capturedPieces.red.forEach(piece => {
        const el = document.createElement('div');
        el.className = 'captured-piece black';
        el.textContent = piece;
        elements.redCaptured.appendChild(el);
    });

    state.capturedPieces.black.forEach(piece => {
        const el = document.createElement('div');
        el.className = 'captured-piece red';
        el.textContent = piece;
        elements.blackCaptured.appendChild(el);
    });
}

async function handlePieceClick(piece, event) {
    event.stopPropagation();

    if (state.isAIThinking) return;

    if (state.gameMode === 'pvp' && piece.color !== state.humanColor && !state.selectedPiece) {
        return;
    }

    if (state.gameMode === 'pvp' && piece.color !== state.humanColor) {
        if (state.selectedPiece && state.validMoves.some(m => m[0] === piece.row && m[1] === piece.col)) {
            await handleMoveClick(piece.row, piece.col);
        }
        return;
    }

    if (piece.color !== state.board.current_player && !state.selectedPiece) {
        return;
    }

    if (state.selectedPiece && 
        state.selectedPiece.row === piece.row && 
        state.selectedPiece.col === piece.col) {
        state.selectedPiece = null;
        state.validMoves = [];
        renderBoard();
        renderValidMoves();
        return;
    }

    state.selectedPiece = piece;
    showLoading('获取可行走法...');
    
    try {
        const response = await apiCall('/moves', 'POST', {
            row: piece.row,
            col: piece.col
        });
        state.validMoves = response.moves;
    } catch (error) {
        console.error('Error fetching moves:', error);
        state.validMoves = [];
    }
    
    hideLoading();
    renderBoard();
    renderValidMoves();
}

async function handleMoveClick(toRow, toCol) {
    if (!state.selectedPiece || state.isAIThinking) return;

    showLoading('执行走法...');
    
    try {
        const response = await apiCall('/move', 'POST', {
            from_row: state.selectedPiece.row,
            from_col: state.selectedPiece.col,
            to_row: toRow,
            to_col: toCol
        });

        if (response.success) {
            state.board = response;
            state.lastMove = {
                from: [state.selectedPiece.row, state.selectedPiece.col],
                to: [toRow, toCol]
            };
            
            if (response.captured) {
                if (state.selectedPiece.color === 'red') {
                    state.capturedPieces.red.push(response.captured);
                } else {
                    state.capturedPieces.black.push(response.captured);
                }
            }
            
            addMessage(response.message, 'success');
            updateGameInfo();
            updateCapturedPieces();
            
            if (response.is_game_over) {
                showGameOver(response.winner_name);
            } else if (state.gameMode === 'pvp' && response.current_player !== state.humanColor) {
                state.isAIThinking = true;
                state.selectedPiece = null;
                state.validMoves = [];
                renderBoard();
                renderValidMoves();
                await makeAIMove();
            }
        } else {
            addMessage(response.message, 'error');
        }
    } catch (error) {
        console.error('Error making move:', error);
        addMessage('走法执行失败', 'error');
    }

    state.selectedPiece = null;
    state.validMoves = [];
    hideLoading();
    renderBoard();
    renderValidMoves();
}

async function makeAIMove() {
    showLoading('AI思考中...');
    
    try {
        const response = await apiCall('/ai/move', 'POST');
        
        if (response.success) {
            state.board = response;
            state.lastMove = {
                from: response.move.from,
                to: response.move.to
            };
            
            if (response.move.captured) {
                state.capturedPieces.black.push(response.move.captured);
            }
            
            addMessage(response.message, 'info');
            updateGameInfo();
            updateCapturedPieces();
            renderBoard();
            
            if (response.is_game_over) {
                showGameOver(response.winner_name);
            }
        } else {
            addMessage(response.message, 'error');
        }
    } catch (error) {
        console.error('Error making AI move:', error);
        addMessage('AI走法执行失败', 'error');
    }

    state.isAIThinking = false;
    hideLoading();
}

function showGameOver(winner) {
    const bodyContent = `
        <div class="game-over-content">
            <div class="game-over-title">游戏结束</div>
            <div class="game-over-winner">${winner || '无'} 获胜！</div>
        </div>
    `;
    
    const footerContent = `
        <button class="btn btn-success" onclick="startNewGame()">再来一局</button>
        <button class="btn btn-secondary" onclick="hideModal()">关闭</button>
    `;
    
    showModal('对局结束', bodyContent, footerContent);
}

async function startPvPGame() {
    const bodyContent = `
        <p>请选择你要执的棋子颜色：</p>
        <div class="color-select">
            <div class="color-option red" data-color="red">
                <div class="color-option-icon">帅</div>
                <div class="color-option-text">红方（先手）</div>
            </div>
            <div class="color-option black" data-color="black">
                <div class="color-option-icon">将</div>
                <div class="color-option-text">黑方（后手）</div>
            </div>
        </div>
    `;
    
    showModal('人机对战', bodyContent);
    
    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', async () => {
            document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
            
            const color = option.dataset.color;
            
            setTimeout(async () => {
                hideModal();
                showLoading('初始化游戏...');
                
                try {
                    const response = await apiCall('/mode', 'POST', {
                        mode: 'pvp',
                        color: color
                    });
                    
                    state.board = response;
                    state.gameMode = 'pvp';
                    state.humanColor = color;
                    state.selectedPiece = null;
                    state.validMoves = [];
                    state.lastMove = null;
                    state.capturedPieces = { red: [], black: [] };
                    
                    addMessage('人机对战模式已开始', 'success');
                    updateGameInfo();
                    updateCapturedPieces();
                    renderBoard();
                    
                    if (color === 'black') {
                        state.isAIThinking = true;
                        await makeAIMove();
                    }
                } catch (error) {
                    console.error('Error starting game:', error);
                    addMessage('游戏初始化失败', 'error');
                }
                
                hideLoading();
            }, 300);
        });
    });
}

async function showPrediction() {
    showLoading('AI预测未来五步...');
    
    try {
        const response = await apiCall('/predict', 'POST', { steps: 5 });
        
        if (response.success && response.predictions.length > 0) {
            let bodyContent = `<div class="prediction-list">`;
            
            response.predictions.forEach((step, index) => {
                const captureText = step.captured ? ` 吃 ${step.captured}` : '';
                bodyContent += `
                    <div class="prediction-item">
                        <div class="prediction-move">
                            第 ${index + 1} 步 (${step.player}): ${step.piece} 
                            (${step.from[0]},${step.from[1]}) → (${step.to[0]},${step.to[1]})
                            ${captureText}
                        </div>
                    </div>
                `;
            });
            
            bodyContent += `</div>`;
            bodyContent += `<p style="margin-top: 20px; font-weight: 600;">预测最终局面评估分: ${response.final_score}</p>`;
            bodyContent += `<p style="color: #6b5344; font-size: 0.9rem;">正数表示红方占优，负数表示黑方占优</p>`;
            
            showModal('预测未来五步', bodyContent);
            addMessage('预测完成', 'success');
        } else {
            addMessage('无法预测有效走法', 'error');
        }
    } catch (error) {
        console.error('Error getting prediction:', error);
        addMessage('预测失败', 'error');
    }
    
    hideLoading();
}

async function showAnalysis() {
    showLoading('AI分析当前局面...');
    
    try {
        const response = await apiCall('/analyze', 'GET');
        
        if (response.success && response.analysis.length > 0) {
            let bodyContent = `
                <div style="margin-bottom: 20px;">
                    <p><strong>当前回合:</strong> ${response.current_player}</p>
                    <p><strong>局面评估分:</strong> ${response.evaluation}</p>
                    <p><strong>红方被将军:</strong> ${response.red_in_check ? '是' : '否'}</p>
                    <p><strong>黑方被将军:</strong> ${response.black_in_check ? '是' : '否'}</p>
                </div>
                <h4 style="margin-bottom: 12px; color: #8b0000;">最佳走法候选 (前10):</h4>
                <div class="analysis-list">
            `;
            
            response.analysis.forEach((item, index) => {
                const captureText = item.captured ? ` 吃 ${item.captured}` : '';
                bodyContent += `
                    <div class="analysis-item">
                        <div class="analysis-move">
                            ${index + 1}. ${item.piece} 
                            (${item.from[0]},${item.from[1]}) → (${item.to[0]},${item.to[1]})
                            ${captureText}
                        </div>
                        <div class="analysis-score">${item.score}</div>
                    </div>
                `;
            });
            
            bodyContent += `</div>`;
            
            showModal('局面分析', bodyContent);
            addMessage('分析完成', 'success');
        } else {
            addMessage('无法分析当前局面', 'error');
        }
    } catch (error) {
        console.error('Error getting analysis:', error);
        addMessage('分析失败', 'error');
    }
    
    hideLoading();
}

async function showRules() {
    showLoading('加载规则...');
    
    try {
        const response = await apiCall('/rules', 'GET');
        
        if (response.success) {
            let bodyContent = `
                <div style="margin-bottom: 20px;">
                    <p><strong>棋盘尺寸:</strong> ${response.board_size}</p>
                    <p><strong>红方位置:</strong> ${response.red_side}</p>
                    <p><strong>黑方位置:</strong> ${response.black_side}</p>
                    <p><strong>楚河汉界:</strong> ${response.river}</p>
                </div>
                <h4 style="margin-bottom: 16px; color: #8b0000;">棋子走法规则:</h4>
            `;
            
            response.rules.forEach(rule => {
                bodyContent += `
                    <div class="rule-item">
                        <div class="rule-name">
                            ${rule.name}
                            <span class="rule-value">价值: ${rule.value}</span>
                        </div>
                        <div class="rule-description">${rule.description}</div>
                    </div>
                `;
            });
            
            showModal('象棋规则', bodyContent);
        }
    } catch (error) {
        console.error('Error getting rules:', error);
        addMessage('加载规则失败', 'error');
    }
    
    hideLoading();
}

async function handleUndo() {
    if (state.isAIThinking) return;
    
    const steps = state.gameMode === 'pvp' ? 2 : 1;
    
    showLoading('悔棋中...');
    
    try {
        const response = await apiCall('/undo', 'POST', { steps });
        
        if (response.success) {
            state.board = response;
            state.selectedPiece = null;
            state.validMoves = [];
            state.lastMove = null;
            
            addMessage(response.message, 'success');
            updateGameInfo();
            renderBoard();
            renderValidMoves();
        } else {
            addMessage('悔棋失败', 'error');
        }
    } catch (error) {
        console.error('Error undoing:', error);
        addMessage('悔棋失败', 'error');
    }
    
    hideLoading();
}

async function handleRestart() {
    if (!confirm('确定要重新开始吗？当前对局进度将会丢失。')) {
        return;
    }
    
    showLoading('重新开始...');
    
    try {
        const response = await apiCall('/restart', 'POST');
        
        if (response.success) {
            state.board = response;
            state.gameMode = 'menu';
            state.selectedPiece = null;
            state.validMoves = [];
            state.lastMove = null;
            state.capturedPieces = { red: [], black: [] };
            state.isAIThinking = false;
            
            addMessage(response.message, 'success');
            updateGameInfo();
            updateCapturedPieces();
            renderBoard();
            renderValidMoves();
        } else {
            addMessage('重新开始失败', 'error');
        }
    } catch (error) {
        console.error('Error restarting:', error);
        addMessage('重新开始失败', 'error');
    }
    
    hideLoading();
}

function handleExit() {
    if (!confirm('确定要退出游戏吗？')) {
        return;
    }
    
    if (confirm('是否关闭当前浏览器窗口？')) {
        window.close();
    }
    
    addMessage('已退出游戏', 'info');
}

async function handleManualMove() {
    const fromRow = parseInt(document.getElementById('input-from-row').value);
    const fromCol = parseInt(document.getElementById('input-from-col').value);
    const toRow = parseInt(document.getElementById('input-to-row').value);
    const toCol = parseInt(document.getElementById('input-to-col').value);

    if (isNaN(fromRow) || isNaN(fromCol) || isNaN(toRow) || isNaN(toCol)) {
        addMessage('请输入完整的坐标', 'error');
        return;
    }

    const piece = state.board.board[fromRow][fromCol];
    if (!piece) {
        addMessage('起始位置没有棋子', 'error');
        return;
    }

    state.selectedPiece = {
        row: fromRow,
        col: fromCol,
        piece: piece,
        color: piece[0] === 'r' ? 'red' : 'black'
    };

    await handleMoveClick(toRow, toCol);

    document.getElementById('input-from-row').value = '';
    document.getElementById('input-from-col').value = '';
    document.getElementById('input-to-row').value = '';
    document.getElementById('input-to-col').value = '';
}

async function startNewGame() {
    hideModal();
    await startPvPGame();
}

async function loadBoard() {
    showLoading('加载棋盘...');
    
    try {
        const response = await apiCall('/board', 'GET');
        state.board = response;
        updateGameInfo();
        renderBoard();
        addMessage('欢迎使用中国象棋 Web UI', 'info');
    } catch (error) {
        console.error('Error loading board:', error);
        addMessage('加载棋盘失败', 'error');
    }
    
    hideLoading();
}

document.addEventListener('click', (e) => {
    if (e.target.closest('.board') && 
        !e.target.closest('.piece') && 
        !e.target.closest('.valid-move')) {
        state.selectedPiece = null;
        state.validMoves = [];
        renderBoard();
        renderValidMoves();
    }
});

document.getElementById('btn-pvp').addEventListener('click', startPvPGame);
document.getElementById('btn-predict').addEventListener('click', showPrediction);
document.getElementById('btn-analyze').addEventListener('click', showAnalysis);
document.getElementById('btn-rules').addEventListener('click', showRules);
document.getElementById('btn-undo').addEventListener('click', handleUndo);
document.getElementById('btn-restart').addEventListener('click', handleRestart);
document.getElementById('btn-exit').addEventListener('click', handleExit);
document.getElementById('btn-move').addEventListener('click', handleManualMove);
document.getElementById('modal-close').addEventListener('click', hideModal);
document.getElementById('modal-overlay').addEventListener('click', (e) => {
    if (e.target === elements.modalOverlay) {
        hideModal();
    }
});

window.startNewGame = startNewGame;
window.hideModal = hideModal;

loadBoard();
