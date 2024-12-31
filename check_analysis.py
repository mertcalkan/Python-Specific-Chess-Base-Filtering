import chess
import chess.pgn

import chess
import chess.pgn

def is_discovered_check(board, move):
    """Check if a move results in a discovered check."""
    board_before_move = board.copy()
    board_before_move.pop()  # Undo last move to analyze previous position
    king_square = board_before_move.king(not board_before_move.turn)  # Opponent's king square

    # Check all attackers of the opponent's king before the move
    for attacker_square in board_before_move.attackers(not board_before_move.turn, king_square):
        # Check if the move opened up a line for the attacker
        if (
            chess.square_file(attacker_square) == chess.square_file(move.from_square) or  # Same file
            chess.square_rank(attacker_square) == chess.square_rank(move.from_square) or  # Same rank
            abs(chess.square_file(attacker_square) - chess.square_file(king_square)) ==
            abs(chess.square_rank(attacker_square) - chess.square_rank(king_square))  # Same diagonal
        ):
            return True
    return False

def is_double_check(board):
    """Check if the current position results in a double check."""
    king_square = board.king(not board.turn)  # Opponent's king square
    return len(board.attackers(not board.turn, king_square)) > 1

def analyze_checks(game):
    """Analyze a game to count various types of checks."""
    board = game.board()
    white_check_count = 0
    black_check_count = 0
    white_double_check_count = 0
    black_double_check_count = 0
    white_discovered_check_count = 0
    black_discovered_check_count = 0

    for move in game.mainline_moves():
        board.push(move)  # Apply the move

        # Check if the move results in a check
        if board.is_check():
            # Determine the player who made the move
            player_making_move = not board.turn  # Previous player made the move

            if player_making_move:  # White made the move
                white_check_count += 1
                if is_discovered_check(board, move):
                    white_discovered_check_count += 1
                if is_double_check(board):
                    white_double_check_count += 1
            else:  # Black made the move
                black_check_count += 1
                if is_discovered_check(board, move):
                    black_discovered_check_count += 1
                if is_double_check(board):
                    black_double_check_count += 1

    return {
        "white_checks": white_check_count,
        "black_checks": black_check_count,
        "white_double_checks": white_double_check_count,
        "black_double_checks": black_double_check_count,
        "white_discovered_checks": white_discovered_check_count,
        "black_discovered_checks": black_discovered_check_count,
    }