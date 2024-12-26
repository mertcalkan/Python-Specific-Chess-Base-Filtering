import chess
import chess.pgn
import chess.engine
import math
import csv
import os

def load_eco_database(eco_directory):
    """
    Load all .tsv files from the provided directory into a list.
    Convert moves from SAN format (with move numbers) to UCI format.
    """
    eco_database = []
    for filename in os.listdir(eco_directory):
        if filename.endswith(".tsv"):
            file_path = os.path.join(eco_directory, filename)
            with open(file_path, "r", encoding="utf-8") as tsvfile:
                reader = csv.reader(tsvfile, delimiter="\t")
                for row in reader:
                    if len(row) >= 3:
                        board = chess.Board()
                        moves = []
                        # Remove move numbers and clean up spaces
                        san_moves = row[2].strip().replace("\n", " ").replace("  ", " ").split(" ")
                        san_moves = [move for move in san_moves if not move.endswith(".")]
                        for move in san_moves:
                            try:
                                uci_move = board.push_san(move).uci()  # Convert SAN to UCI
                                moves.append(uci_move)
                            except ValueError:
                                print(f"Invalid move '{move}' in ECO '{row[0]} - {row[1]}'")
                                break  # Skip invalid openings
                        if not moves:
                            print(f"Skipping ECO '{row[0]} - {row[1]}' due to empty moves.")
                            continue
                        eco_database.append({
                            "eco": row[0].strip(),
                            "name": row[1].strip(),
                            "moves": moves
                        })
    return eco_database



def get_opening_name_and_code(board, eco_database):
    """
    Determine the opening name and ECO code based on the game's moves using the loaded ECO database.
    """
    game_moves = [move.uci() for move in board.move_stack]
    print("Game Moves (UCI):", game_moves)

    for opening in eco_database:
        opening_moves = opening["moves"]
        print("Checking ECO Code:", opening["eco"])
        print("Opening Name:", opening["name"])
        print("Opening Moves (UCI):", opening_moves)

        # Eşleşme kontrolü
        if game_moves[:len(opening_moves)] == opening_moves:
            print("Matched Opening:", opening["eco"], opening["name"])
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

    # Determine opening name and ECO code
    eco_code, opening_name = get_opening_name_and_code(board, eco_database)
    results['OpeningName'] = opening_name
    results['ECOCode'] = eco_code

    # Assign castling results
    results['WhiteCastling'] = white_castled
    results['BlackCastling'] = black_castled
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
pgn_file = "PgnFiles/tal_kasparov.pgn"  # Path to the PGN file
stockfish_path = "stockfish.exe"  # Path to the Stockfish engine
eco_directory = "OpeningCodes/tsv"  # Path to the directory containing .tsv files

game_analysis = analyze_pgn(pgn_file, stockfish_path, eco_directory)
print(game_analysis)

