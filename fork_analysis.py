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
    """Detect if the given move creates a fork or exposes the player to a fork."""
    fork_targets = []
    counter_fork_targets = []
    attacker_square = move.to_square
    attacking_piece = board.piece_at(attacker_square)

    if attacking_piece:
        attacked_squares = board.attacks(attacker_square)

        # Check each attacked square
        for square in attacked_squares:
            target_piece = board.piece_at(square)
            if target_piece and target_piece.color != attacking_piece.color:  # Enemy piece
                # Check if the target is pinned
                is_pinned = board.is_pinned(target_piece.color, square)
                # Check if the target square is protected
                is_protected_status = is_protected(board, square, attacking_piece.color)
                is_forcing = target_piece.piece_type == chess.KING  
                
                # Add target only if it's not pinned and meets other conditions
                if not is_pinned and (not is_protected_status or is_forcing):
                    fork_targets.append((square, target_piece.symbol(), PIECE_VALUES[target_piece.piece_type]))

        # Check if the attacker itself becomes exposed to a fork
        for opponent_move in board.legal_moves:
            temp_board = board.copy()
            temp_board.push(opponent_move)
            opponent_attacker = temp_board.piece_at(opponent_move.to_square)
            if opponent_attacker and opponent_attacker.color != attacking_piece.color:
                opponent_attacked_squares = temp_board.attacks(opponent_move.to_square)
                for opponent_square in opponent_attacked_squares:
                    opponent_target_piece = temp_board.piece_at(opponent_square)
                    if (
                        opponent_target_piece
                        and opponent_target_piece.color == attacking_piece.color
                        and opponent_target_piece.piece_type != chess.KING
                    ):
                        counter_fork_targets.append(
                            (opponent_square, opponent_target_piece.symbol(), PIECE_VALUES[opponent_target_piece.piece_type])
                        )

        # Check if the attacker is safe
        attacker_is_safe = all(
            PIECE_VALUES[attacking_piece.piece_type] >= PIECE_VALUES[board.piece_at(attacker).piece_type]
            for attacker in board.attackers(not attacking_piece.color, attacker_square)
        )

        # Add a check for fork validity when targets are defended
        fork_is_valid = True
        for square, symbol, value in fork_targets:
            defenders = board.attackers(not attacking_piece.color, square)
            for defender in defenders:
                defender_piece = board.piece_at(defender)
                if defender_piece and PIECE_VALUES[defender_piece.piece_type] <= value:
                    fork_is_valid = False

        # Check if at least two valuable targets are threatened
        if len(fork_targets) >= 2 and attacker_is_safe and fork_is_valid:
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
                "counter_fork": len(counter_fork_targets) >= 2,  # Exposed to counter-fork
                "counter_fork_targets": [
                    {
                        "target_piece": target[1],
                        "position": chess.square_name(target[0]),
                        "value": target[2],
                    }
                    for target in counter_fork_targets
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

    return {
        "White fork count": white_fork_count,
        "White fork details": white_fork_details,
        "Black fork count": black_fork_count,
        "Black fork details": black_fork_details,
    }