import chess
import chess.pgn

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # King cannot be captured but is essential for fork types
}

def is_protected(board, square, attacker_color):
    """Check if a square is protected by the opponent."""
    opponent_color = not attacker_color
    return any(board.is_attacked_by(opponent_color, sq) for sq in [square])

def detect_fork_on_move(board, move):
    """Detect if the given move creates a fork."""
    fork_targets = []
    attacker_square = move.to_square
    attacking_piece = board.piece_at(attacker_square)

    if attacking_piece:
        attacked_squares = board.attacks(attacker_square)

        # Check if the move attacks at least two valuable enemy pieces
        for square in attacked_squares:
            target_piece = board.piece_at(square)
            if target_piece and target_piece.color != attacking_piece.color:  # Enemy piece
                is_protected_status = is_protected(board, square, attacking_piece.color)
                can_be_taken = board.is_attacked_by(target_piece.color, attacker_square)  # Attacker can be taken
                is_forcing = target_piece.piece_type == chess.KING  # Check if it's a forcing move (e.g., check)
                
                # Include target if it's not protected or is forcing, and attacker cannot be easily taken
                if (not is_protected_status or is_forcing) and not can_be_taken:
                    fork_targets.append((square, target_piece.symbol(), PIECE_VALUES[target_piece.piece_type]))
        
        # Filter targets: Only count as a fork if there are at least two valuable or forcing targets
        if len(fork_targets) >= 2:
            return {
                "attacker": attacking_piece.symbol(),
                "attacker_square": chess.square_name(attacker_square),
                "targets": [
                    {
                        "target_piece": target[1],
                        "position": chess.square_name(target[0]),
                        "value": target[2],
                        "protected": is_protected(board, target[0], attacking_piece.color),
                    }
                    for target in fork_targets
                ],
            }
    return None

def format_fork_details(fork_details):
    """Format fork details to show the attacker, its position, and targets in a readable way."""
    formatted_details = []
    for fork in fork_details:
        attacker = fork["attacker"]
        attacker_square = fork["attacker_square"]
        targets = fork["targets"]

        # Format targets
        target_descriptions = [
            f"{target['target_piece']}{target['position']} (Value: {target['value']}, Protected: {'Yes' if target['protected'] else 'No'})"
            for target in targets
        ]

        # Combine into a formatted string
        formatted_details.append(
            f"Attacker: {attacker}{attacker_square}, Targets: {', '.join(target_descriptions)}"
        )
    return formatted_details


def analyze_forks(game):
    """Analyze a chess game for forks based on played moves."""
    board = game.board()
    white_fork_count = 0
    black_fork_count = 0
    white_fork_details = []
    black_fork_details = []

    # Process each move in the game
    for move in game.mainline_moves():
        board.push(move)  # Play the move
        fork = detect_fork_on_move(board, move)  # Detect fork caused by this move

        if fork:
            if board.turn:  # If it's White's turn, the previous move was Black's
                black_fork_count += 1
                black_fork_details.append(fork)
            else:
                white_fork_count += 1
                white_fork_details.append(fork)

    # Format fork details for output
    formatted_white_fork_details = format_fork_details(white_fork_details)
    formatted_black_fork_details = format_fork_details(black_fork_details)

    return {
        "White fork count": white_fork_count,
        "White fork details": formatted_white_fork_details if white_fork_count > 0 else None,
        "Black fork count": black_fork_count,
        "Black fork details": formatted_black_fork_details if black_fork_count > 0 else None,
    }
