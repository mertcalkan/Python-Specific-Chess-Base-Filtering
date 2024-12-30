import chess
import os
import csv

def load_eco_database(eco_directory):
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
                        san_moves = row[2].strip().replace("\n", " ").replace("  ", " ").split(" ")
                        san_moves = [move for move in san_moves if not move.endswith(".")]
                        for move in san_moves:
                            try:
                                uci_move = board.push_san(move).uci()
                                moves.append(uci_move)
                            except ValueError:
                                print(f"Invalid move '{move}' in ECO '{row[0]} - {row[1]}'")
                                break
                        eco_database.append({
                            "eco": row[0].strip(),
                            "name": row[1].strip(),
                            "moves": moves,
                            "final_fen": board.board_fen()
                        })
    return eco_database

def get_opening_name_and_code(board, eco_database):
    game_moves = [move.uci() for move in board.move_stack]
    best_match = {"eco": "Unknown", "name": "Unknown", "length": 0}

    for opening in eco_database:
        if game_moves[:len(opening["moves"])] == opening["moves"]:
            if len(opening["moves"]) > best_match["length"]:
                best_match = {
                    "eco": opening["eco"],
                    "name": opening["name"],
                    "length": len(opening["moves"])
                }

    return best_match["eco"], best_match["name"]
