import chess
# piyon yapısının ne kadar sürede kaybolduğu gibi etkenler incelenecek.
def analyze_doubled_tripled_pawns(game):
    """
    Analyze a chess game to find doubled and tripled pawns for both sides,
    accounting for resolved pawn structures, and return positions in notation.
    """
    board = game.board()
    white_doubled_pawns = set()
    black_doubled_pawns = set()
    white_tripled_pawns = set()
    black_tripled_pawns = set()

    # Track previously identified structures
    tracked_white_doubled = set()
    tracked_black_doubled = set()
    tracked_white_tripled = set()
    tracked_black_tripled = set()

    # Iterate through all moves in the game
    for move in game.mainline_moves():
        board.push(move)

        # Track files for each color
        white_files = {file: [] for file in range(8)}  # Files 0 (a) to 7 (h) for White
        black_files = {file: [] for file in range(8)}  # Files 0 (a) to 7 (h) for Black

        # Identify pawns on the board
        for square, piece in board.piece_map().items():
            if piece.piece_type == chess.PAWN:  # Check only pawns
                file = chess.square_file(square)  # Get the file of the pawn
                if piece.color == chess.WHITE:
                    white_files[file].append(square)
                else:
                    black_files[file].append(square)

        # Check White's files for doubled and tripled pawns
        for file, squares in white_files.items():
            if len(squares) > 1:  # At least 2 pawns on the same file
                doubled_structure = tuple(sorted(squares))
                if doubled_structure not in tracked_white_doubled:
                    white_doubled_pawns.add(tuple(chess.square_name(sq) for sq in doubled_structure))
                    tracked_white_doubled.add(doubled_structure)

            if len(squares) > 2:  # At least 3 pawns on the same file
                tripled_structure = tuple(sorted(squares))
                if tripled_structure not in tracked_white_tripled:
                    white_tripled_pawns.add(tuple(chess.square_name(sq) for sq in tripled_structure))
                    tracked_white_tripled.add(tripled_structure)

        # Check Black's files for doubled and tripled pawns
        for file, squares in black_files.items():
            if len(squares) > 1:  # At least 2 pawns on the same file
                doubled_structure = tuple(sorted(squares))
                if doubled_structure not in tracked_black_doubled:
                    black_doubled_pawns.add(tuple(chess.square_name(sq) for sq in doubled_structure))
                    tracked_black_doubled.add(doubled_structure)

            if len(squares) > 2:  # At least 3 pawns on the same file
                tripled_structure = tuple(sorted(squares))
                if tripled_structure not in tracked_black_tripled:
                    black_tripled_pawns.add(tuple(chess.square_name(sq) for sq in tripled_structure))
                    tracked_black_tripled.add(tripled_structure)

        # Remove resolved structures
        resolved_white_doubled = {structure for structure in tracked_white_doubled if not all(board.piece_at(square) for square in structure)}
        resolved_black_doubled = {structure for structure in tracked_black_doubled if not all(board.piece_at(square) for square in structure)}
        resolved_white_tripled = {structure for structure in tracked_white_tripled if not all(board.piece_at(square) for square in structure)}
        resolved_black_tripled = {structure for structure in tracked_black_tripled if not all(board.piece_at(square) for square in structure)}

        # Update tracked structures
        tracked_white_doubled -= resolved_white_doubled
        tracked_black_doubled -= resolved_black_doubled
        tracked_white_tripled -= resolved_white_tripled
        tracked_black_tripled -= resolved_black_tripled

    # Return the results
    return {
        "white_doubled_pawns_count": len(white_doubled_pawns),
        "black_doubled_pawns_count": len(black_doubled_pawns),
        "white_tripled_pawns_count": len(white_tripled_pawns),
        "black_tripled_pawns_count": len(black_tripled_pawns),
        "white_doubled_pawns_positions": white_doubled_pawns,
        "black_doubled_pawns_positions": black_doubled_pawns,
        "white_tripled_pawns_positions": white_tripled_pawns,
        "black_tripled_pawns_positions": black_tripled_pawns,
    }
