from pgn_utils import load_pgn
from eco_utils import load_eco_database
from stockfish_utils import connect_stockfish, disconnect_stockfish
from basic_analysis import analyze_game
from fork_analysis import analyze_forks
from check_analysis import analyze_checks
def main():
    pgn_file = "PgnFiles/fischer_tal_1959.pgn"
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
   
    print(results)

    # Stockfish bağlantısını kapat
    disconnect_stockfish(engine)

if __name__ == "__main__":
    main()
