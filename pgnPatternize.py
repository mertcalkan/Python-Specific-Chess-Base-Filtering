import chess
import chess.pgn
import chess.engine
import os
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
    white_castling = {"short": False, "long": False}
    black_castling = {"short": False, "long": False}
    move_count = 0
    draw_type = None
    winning_method = None
    
    board = game.board()
    
    # Analyze moves
    for move in game.mainline_moves():
        move_count += 1
        board.push(move)
        
        # Check castling
        if board.is_castling(move):
            if board.turn:  # True = White's turn after move
                if move.to_square in [chess.G1, chess.G8]:  # Short castling
                    white_castling["short"] = True
                elif move.to_square in [chess.C1, chess.C8]:  # Long castling
                    white_castling["long"] = True
            else:
                if move.to_square in [chess.G1, chess.G8]:
                    black_castling["short"] = True
                elif move.to_square in [chess.C1, chess.C8]:
                    black_castling["long"] = True

    # Simplify castling results
    results['WhiteCastling'] = "Short" if white_castling["short"] else "Long" if white_castling["long"] else "Not Castled"
    results['BlackCastling'] = "Short" if black_castling["short"] else "Long" if black_castling["long"] else "Not Castled"

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
    
    results['TotalMoves'] = math.floor(move_count /2)
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
