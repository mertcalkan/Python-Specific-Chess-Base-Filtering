import chess
import chess.pgn
import chess.engine
import csv
import os
import math

def load_eco_database(eco_directory):
    """
    Load all .tsv files from the provided directory into a dictionary.
    Each key is an ECO code, and the value is a tuple of (Opening Name, Moves List).
    """
    eco_database = []
    for filename in os.listdir(eco_directory):
        if filename.endswith(".tsv"):
            file_path = os.path.join(eco_directory, filename)
            with open(file_path, "r", encoding="utf-8") as tsvfile:
                reader = csv.reader(tsvfile, delimiter="\t")
                for row in reader:
                    if len(row) >= 3:  # Ensure the row has ECO code, name, and moves
                        eco_database.append({
                            "eco": row[0],
                            "name": row[1],
                            "moves": row[2].split()  # Convert moves into a list
                        })
    return eco_database

def get_opening_name_and_code(board, eco_database):
    """
    Determine the opening name and ECO code based on the game's moves using the loaded ECO database.
    """
    for opening in eco_database:
        temp_board = chess.Board()
        for move_uci in opening["moves"]:
            move = chess.Move.from_uci(move_uci)
            if move in temp_board.legal_moves:
                temp_board.push(move)
            else:
                break
            # Check if the board position matches
            if temp_board.board_fen() == board.board_fen():
                return opening["eco"], opening["name"]
    return "Unknown", "Unknown"

def analyze_pgn(pgn_file_path, stockfish_path, eco_directory):
    results = {}

    # Load ECO database
    eco_database = load_eco_database(eco_directory)

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
    board = game.board()
    move_count = 0
    draw_type = None
    winning_method = None
    resignation_analysis = None
    
    # Analyze moves
    for move in game.mainline_moves():
        move_count += 1
        board.push(move)

    # Determine opening name and ECO code
    eco_code, opening_name = get_opening_name_and_code(board, eco_database)
    results['OpeningName'] = opening_name
    results['ECOCode'] = eco_code

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

# Example usage
pgn_file = "PgnFiles/Kirilmaz.pgn"
stockfish_path = "stockfish.exe"
eco_directory = "OpeningCodes/tsv"  # Path to the folder containing a.tsv, b.tsv, c.tsv, etc.

game_analysis = analyze_pgn(pgn_file, stockfish_path, eco_directory)
print(game_analysis)
