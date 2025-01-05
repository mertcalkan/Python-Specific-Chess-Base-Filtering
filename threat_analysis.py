import chess
import chess.engine
import chess.pgn

def analyze_threat_moves(game, engine_path):
    """
    Analyze threat moves in a chess game.
    """
    # Initialize board and engine
    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    white_threat_moves = []
    black_threat_moves = []
    white_threat_count = 0
    black_threat_count = 0
    is_threat = False
    for move in game.mainline_moves():
        # Apply the move to the board
        board.push(move)
        
        # Analyze the position after the move but give the turn back to the moving side
        with engine.analysis(board, chess.engine.Limit(depth=20)) as analysis:
            info = analysis.get()
            if "score" in info:
                score = info["score"].relative
                if score.is_mate():
                    is_threat = True  # Mating threat
                else:
                    advantage = score.score()
                    if advantage > 300:  # Significant advantage (for White)
                        is_threat = board.turn  # If White's turn, it was a Black threat move
                    elif advantage < -300:  # Significant advantage (for Black)
                        is_threat = not board.turn  # If Black's turn, it was a White threat move
                    else:
                        is_threat = False

        # Record the threat move
        if is_threat:
            move_san = board.san(move)
            if board.turn:  # Black's turn, White's last move was a threat
                white_threat_moves.append(move_san)
                white_threat_count += 1
            else:  # White's turn, Black's last move was a threat
                black_threat_moves.append(move_san)
                black_threat_count += 1

    engine.quit()

    return {
        "white_threat_count": white_threat_count,
        "black_threat_count": black_threat_count,
        "white_threat_moves": white_threat_moves,
        "black_threat_moves": black_threat_moves,
    }

