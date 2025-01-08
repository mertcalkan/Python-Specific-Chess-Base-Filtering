import chess
import chess.pgn
import chess.engine

def is_zugzwang(board, engine):
    """
    Check if the current position is a Zugzwang.
    """
    # Get evaluation for the current position
    initial_info = engine.analyse(board, chess.engine.Limit(depth=20))
    initial_eval = initial_info["score"].relative.score()

    if initial_eval is None:
        return False  # If evaluation is unavailable, it's not Zugzwang

    # Check all legal moves
    for move in board.legal_moves:
        board.push(move)
        try:
            new_info = engine.analyse(board, chess.engine.Limit(depth=15))
            new_eval = new_info["score"].relative.score()
        finally:
            board.pop()
    
        if new_eval is not None and new_eval >= initial_eval:
            return False

    # If all moves worsen the position, it's Zugzwang
    return True

def find_zugzwang_positions(pgn_file_path, stockfish_path):
    """
    Find Zugzwang positions in a PGN file.
    """
    with open(pgn_file_path) as pgn_file, chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
        zugzwang_positions = []
        game = chess.pgn.read_game(pgn_file)

        while game:
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                if is_zugzwang(board, engine) :
                    zugzwang_positions.append({
                        "fen": board.fen(),
                        "zugzwang_side": "White" if board.turn == chess.WHITE else "Black",
                        "last_move": move
                    })

            game = chess.pgn.read_game(pgn_file)
    return {"zugzwang_moments": zugzwang_positions}

def correct_sides(result,board):
    if result == "1-0" and not board.turn or result == "0-1" and board.turn:
        return True
    else:
        return False