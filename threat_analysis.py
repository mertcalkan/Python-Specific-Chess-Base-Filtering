import chess
import chess.engine

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: float('inf')
}

def is_material_gain_threat(board, move, engine):
    """
    Check if a move creates a threat for material gain.
    """
    board.push(move)  # Apply the move
    threats = []

    # Analyze the current board position after the move
    for square, piece in board.piece_map().items():
        if piece.color != board.turn:  # Opponent's pieces
            defenders = board.attackers(not piece.color, square)
            attackers = board.attackers(piece.color, square)

            if attackers and (not defenders or len(attackers) > len(defenders)):
                # Check if the attacked piece can be captured for material gain
                piece_value = PIECE_VALUES[piece.piece_type]
                defender_value = min(
                    (PIECE_VALUES[board.piece_at(defender).piece_type] for defender in defenders),
                    default=float('inf')  # If no defenders, set to infinity
                )
                if piece_value > defender_value:
                    threats.append((square, piece_value, defender_value))

    board.pop()  # Undo the move
    return threats

def analyze_game_material_threats(game, stockfish_path):
    """
    Analyze a game to find moves that create material gain threats.
    """
    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
        board = game.board()
        threats = {"white_threats": [], "black_threats": []}

        for move in game.mainline_moves():
            material_threats = is_material_gain_threat(board, move, engine)

            if material_threats:
                if board.turn:  # Black's move
                    threats["black_threats"].append((board.san(move), material_threats))
                else:  # White's move
                    threats["white_threats"].append((board.san(move), material_threats))

            board.push(move)

    return threats

