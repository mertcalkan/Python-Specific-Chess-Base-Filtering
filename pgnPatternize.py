import chess
import chess.pgn
import chess.engine
import math
def analyze_pgn(pgn_file_path, stockfish_path):
    results = {}
    
    # Open the PGN file
    with open(pgn_file_path, 'r') as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    
    # Extract basic game info
    results['White'] = game.headers.get("White", "Unknown")
    results['Black'] = game.headers.get("Black", "Unknown")
    results['WhiteElo'] = game.headers.get("WhiteElo", "Unknown")
    results['BlackElo'] = game.headers.get("BlackElo", "Unknown")
    results['Result'] = game.headers.get("Result", "Unknown")
    
    # Connect to Stockfish
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    
    # Initialize analysis variables
    white_castled = "Not Castled"
    black_castled = "Not Castled"
    move_count = 0
    draw_type = None
    winning_method = None
    
    board = game.board()
    
    # Analyze moves
    for move in game.mainline_moves():
        move_count += 1

        # Detect castling moves
        if board.is_kingside_castling(move):
            if board.turn:  # If it's black's turn after move, white castled
                white_castled = "Short"
            else:  # If it's white's turn after move, black castled
                black_castled = "Short"
        elif board.is_queenside_castling(move):
            if board.turn:  # If it's black's turn after move, white castled
                white_castled = "Long"
            else:  # If it's white's turn after move, black castled
                black_castled = "Long"
        
        board.push(move)

    # Assign castling results
    results['WhiteCastling'] = white_castled
    results['BlackCastling'] = black_castled

    # Determine game result
    result = game.headers.get("Result", "Unknown")
    if result == "1-0":
        results['Winner'] = "White"
    elif result == "0-1":
        results['Winner'] = "Black"
    elif result == "1/2-1/2":
        results['Winner'] = "Draw"
        # Check type of draw
        if board.is_stalemate():
            draw_type = "Stalemate"
        elif board.is_repetition():
            draw_type = "Threefold Repetition"
        elif board.is_insufficient_material():
            draw_type = "Insufficient Material"
        else:
            draw_type = "Agreement"
    
    # If the game ended with a winner, determine the winning method
    if result in ["1-0", "0-1"]:
        last_move = board.pop()
        if board.is_checkmate():
            winning_method = "Checkmate"
        else:
            winning_method = "Resignation"
        board.push(last_move)  # Restore the board state
    
    results['TotalMoves'] = math.floor(move_count / 2) 
    results['DrawType'] = draw_type
    results['WinningMethod'] = winning_method

    # Close the Stockfish engine
    engine.quit()

    return results


# Example usage
pgn_file = "PgnFiles/tal_kasparov.pgn"  # Replace with your PGN file path
stockfish_path = "stockfish.exe"  # Replace with your Stockfish path

game_analysis = analyze_pgn(pgn_file, stockfish_path)
print(game_analysis)
