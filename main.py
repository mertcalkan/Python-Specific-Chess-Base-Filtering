from pgn_utils import load_pgn
from eco_utils import load_eco_database
from stockfish_utils import connect_stockfish, disconnect_stockfish
from basic_analysis import analyze_game
from fork_analysis import analyze_forks
from check_analysis import analyze_checks
from en_passant import count_en_passant_moves
from pawn_structure import analyze_doubled_tripled_pawns
from threat_analysis import analyze_game_material_threats
from zugzwang_analysis import find_zugzwang_positions
def main():
    pgn_file = "PgnFiles/Zugzwang/Friedrich S&auml;emisch  _vs_Aron Nimzowitsch_1923.__.__.pgn"
    stockfish_path = "stockfish.exe"
    eco_directory = "OpeningCodes/tsv"

    # ECO veritabanını yükle
    eco_database = load_eco_database(eco_directory)

    # PGN dosyasını yükle
    game = load_pgn(pgn_file)

    # Stockfish'e bağlan
    engine = connect_stockfish(stockfish_path)

    # Maçı analiz et
    results = analyze_game(game, engine, eco_database)
    # fork_results = analyze_forks(game)
    # results.update(fork_results)
    check_results = analyze_checks(game)
    results.update(check_results )
    en_passant_stats = count_en_passant_moves(game)
    results.update(en_passant_stats)
    # threats = analyze_game_material_threats(game,stockfish_path)
    # results.update(threats)
    zugzwangs = find_zugzwang_positions(pgn_file,stockfish_path)
    results.update(zugzwangs)
    print(results)

    # Stockfish bağlantısını kapat
    disconnect_stockfish(engine)

if __name__ == "__main__":
    main()
