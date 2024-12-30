import requests
import chess
import chess.pgn
import urllib.parse
import io

def get_opening_stats(fen, time_control, rating):
    url = "https://explorer.lichess.ovh/lichess"
    params = {
        "fen": fen,
        "speeds": time_control,
        "ratings": rating,
    }
    
    encoded_params = urllib.parse.urlencode(params)
    full_url = f"{url}?{encoded_params}"
    
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Lichess API: {e}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        print(f"Full URL: {full_url}")
        return None

def get_best_move(stats):
    moves = stats.get("moves", [])
    if not moves:
        return None
    
    best_move = max(moves, key=lambda m: (m["white"] + 0.5 * m["draws"]) / (m["white"] + m["draws"] + m["black"]))
    return best_move["san"]

def get_valid_responses(stats, min_probability=0.05):
    moves = stats.get("moves", [])
    if not moves:
        return []
    
    total_games = sum(move["white"] + move["draws"] + move["black"] for move in moves)
    return [move["san"] for move in moves if (move["white"] + move["draws"] + move["black"]) / total_games >= min_probability]

def create_variation_tree(node, board, depth, time_control, rating, is_player_turn=True):
    if depth == 0:
        return

    stats = get_opening_stats(board.fen(), time_control, rating)
    if stats is None:
        return

    if is_player_turn:
        # Player's move (White)
        best_move = get_best_move(stats)
        if best_move is None:
            return
        new_node = node.add_variation(board.parse_san(best_move))
        new_board = board.copy()
        new_board.push_san(best_move)
        create_variation_tree(new_node, new_board, depth - 1, time_control, rating, False)
    else:
        # Opponent's moves (Black)
        valid_responses = get_valid_responses(stats)
        for response in valid_responses:
            new_node = node.add_variation(board.parse_san(response))
            new_board = board.copy()
            new_board.push_san(response)
            create_variation_tree(new_node, new_board, depth - 1, time_control, rating, True)

def create_pgn(depth, time_control, rating):
    game = chess.pgn.Game()
    game.headers["Event"] = "Lichess Opening Explorer"
    game.headers["Site"] = "https://lichess.org/"
    game.headers["Date"] = "????.??.??"
    game.headers["Round"] = "-"
    game.headers["White"] = "Player"
    game.headers["Black"] = "Opponent"
    game.headers["Result"] = "*"

    board = chess.Board()
    create_variation_tree(game, board, depth, time_control, rating)

    return game

def main():
    fen = input("Enter FEN (press Enter for starting position): ").strip()
    if not fen:
        fen = chess.STARTING_FEN
    
    time_control = input("Enter time control (bullet,blitz,rapid,classical or leave empty for all): ").strip().lower()
    if not time_control:
        time_control = "bullet,blitz,rapid,classical"
    
    min_rating = input("Enter minimum rating (1600,1800,2000,2200,2500 or leave empty for all): ").strip()
    if not min_rating:
        rating = "0,1600,1800,2000,2200,2500"
    else:
        rating = f"{min_rating},2500"
    
    depth = int(input("Enter the depth of variations to explore: "))
    
    print("\nGenerating PGN...")
    game = create_pgn(depth, time_control, rating)
    
    pgn_string = io.StringIO()
    exporter = chess.pgn.FileExporter(pgn_string)
    game.accept(exporter)
    
    with open("generated_variations.pgn", "w") as pgn_file:
        pgn_file.write(pgn_string.getvalue())
    
    print("PGN file 'generated_variations.pgn' has been created.")
    print("\nGenerated PGN:")
    print(pgn_string.getvalue())

if __name__ == "__main__":
    main()