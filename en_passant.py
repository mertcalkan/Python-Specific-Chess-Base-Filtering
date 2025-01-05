import chess
import chess.pgn

def count_en_passant_moves(game):
    """
    Count the number of en passant moves made by White and Black in a chess game.
    
    Args:
        game: A chess.pgn.Game object representing the game to analyze.

    Returns:
        A dictionary with counts of en passant moves for White and Black.
    """
    board = game.board()
    white_en_passant_count = 0
    black_en_passant_count = 0

    for move in game.mainline_moves():
        if board.is_en_passant(move):
            if not board.turn: 
                black_en_passant_count += 1
            else:  
                white_en_passant_count += 1

        # Push the move to update the board
        board.push(move)

    return {
        "white_en_passant_count": white_en_passant_count,
        "black_en_passant_count": black_en_passant_count
    }