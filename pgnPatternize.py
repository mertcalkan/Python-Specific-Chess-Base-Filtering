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
    resignation_analysis = None  # Analysis of resignation decision
    
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
 
    if result == "1/2-1/2":
        
        if board.is_stalemate():
            draw_type = "Stalemate"
        elif board.is_repetition():
            draw_type = "Threefold Repetition"
        elif board.is_insufficient_material():
            draw_type = "Insufficient Material"
        else:
            draw_type = "Agreement"
    
 
    if result in ["1-0", "0-1"]:
        if board.is_checkmate(): 
            winning_method = "Checkmate"
        else:
            winning_method = "Resignation"
            evaluation = engine.analyse(board, chess.engine.Limit(time=1))  
            score = evaluation['score'].relative
            
            if score.is_mate():
                resignation_analysis = "Correct, opponent has a forced mate."
            else:
                score_value = score.score(mate_score=10000) 
                if (result == "1-0" and score_value < 0) or (result == "0-1" and score_value > 0):
                    resignation_analysis = "Incorrect, resigning side was better."
                elif abs(score_value) < 50:
                    resignation_analysis = "Incorrect, the position was close to a draw."
                else:
                    resignation_analysis = "Correct, position was losing."
    
    results['TotalMoves'] = math.floor(move_count / 2)
    results['DrawType'] = draw_type
    results['WinningMethod'] = winning_method
    results['ResignationAnalysis'] = resignation_analysis
    engine.quit()

    return results



pgn_file = "PgnFiles/stalemate.pgn" 
stockfish_path = "stockfish.exe" 

game_analysis = analyze_pgn(pgn_file, stockfish_path)
print(game_analysis)
