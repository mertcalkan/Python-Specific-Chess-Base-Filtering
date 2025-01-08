import chess
import chess.pgn

import chess
import chess.pgn

def is_discovered_check(board, move):
    """
    Determine if a move results in a discovered check.
    A discovered check occurs when a piece moves, uncovering an attack by another piece (bishop, rook, or queen).
    """
    # Copy the board state before the move
    board_before_move = board.copy()
    board_before_move.pop()  # Undo the last move to analyze the position before the move

    # Determine the side that gave the check
    is_white_turn = board.turn  # If it's White's turn, Black just moved
    opponent_king_square = board_before_move.king(is_white_turn)  # Opponent's king square

    if opponent_king_square is None:  # No king found (invalid state)
        return False

    # The square the moving piece moved from
    moving_piece_square = move.from_square

    
    for attacker_square, piece in board_before_move.piece_map().items():
        if (
            piece.color != board.turn  # Rakip taşlar
            and piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]  # Açarak şahı oluşturabilecek taşlar
        ):
            # Check if there's a direct line of attack to the king
            ray = chess.SquareSet(chess.ray(attacker_square, opponent_king_square) or [])
            if not ray:  # No direct line
                continue

       
            if moving_piece_square in ray:
                if board.is_attacked_by(piece.color, opponent_king_square):
               
                    if moving_piece_square != attacker_square:
                        print(f"Discovered check detected: Attacker {piece.symbol()} at {chess.square_name(attacker_square)}, King at {chess.square_name(opponent_king_square)}")
                        return True  # Açarak şahı tespit edildis

    return False


def is_double_check(board, move):
    """Check if the move results in a double check."""
    board_before_move = board.copy()
    board_before_move.pop() 
    king_square = board_before_move.king(not board_before_move.turn)  

   
    pre_move_attackers = list(board_before_move.attackers(not board_before_move.turn, king_square))
    
   
    post_move_attackers = list(board.attackers(not board.turn, king_square))
    
    # Double check happens if:
    # 1. After the move, there are two or more attackers.
    # 2. At least one of these attackers was NOT threatening the king before the move.
    if len(post_move_attackers) > 1 and len(pre_move_attackers) < len(post_move_attackers):
        return True
    return False


def analyze_checks(game):
    """Analyze the game to count checks, double checks, and discovered checks."""
    board = game.board()
    white_checks = 0
    black_checks = 0
    white_double_checks = 0
    black_double_checks = 0
    white_discovered_checks = 0
    black_discovered_checks = 0
    wh_dc = []
    bl_dc = []
    for move in game.mainline_moves():
        board.push(move)

        if board.is_check():
            # Debug: Print the move and the check
            # print(f"Check detected: {move}, Turn: {'White' if board.turn else 'Black'}")

            if not board.turn:  # White gave check
                white_checks += 1
                if is_discovered_check(board, move):
                    wh_dc.append(move)
                    white_discovered_checks += 1
                if is_double_check(board, move):
                    white_double_checks += 1
            else:  # Black gave check
                black_checks += 1
                if is_discovered_check(board, move):
                    bl_dc.append(move)
                    black_discovered_checks += 1
                if is_double_check(board, move):
                    black_double_checks += 1

    return {
        "white_checks": white_checks,
        "black_checks": black_checks,
        "white_double_checks": white_double_checks,
        "black_double_checks": black_double_checks,
        "white_discovered_checks": white_discovered_checks,
        "black_discovered_checks": black_discovered_checks,
        "whdc" : wh_dc,
        "bldc" : bl_dc
       
    }
