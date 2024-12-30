import chess.pgn

def load_pgn(pgn_file_path):
    with open(pgn_file_path, "r") as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    if not game:
        raise ValueError("No valid game found in the PGN file.")
    return game
