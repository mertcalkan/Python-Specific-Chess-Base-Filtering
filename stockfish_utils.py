import chess.engine

def evaluate_position(engine, board):
    return engine.analyse(board, chess.engine.Limit(time=0.1))

def connect_stockfish(stockfish_path):
    return chess.engine.SimpleEngine.popen_uci(stockfish_path)

def disconnect_stockfish(engine):
    engine.quit()
