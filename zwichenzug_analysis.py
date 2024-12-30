from stockfish_utils import evaluate_position
import chess
import chess.pgn
def analyze_zwischenzugs(game, engine):
    board = game.board()

    white_zwischenzug_count = 0
    black_zwischenzug_count = 0
    white_zwischenzug_types = []
    black_zwischenzug_types = []

    for move in game.mainline_moves():
        current_turn = "White" if board.turn else "Black"
        board.push(move)

        previous_eval = evaluate_position(engine, board)
        previous_score = previous_eval['score'].relative

        opponent_moves = list(board.legal_moves)
        zwischenzug_detected = False
        zwischenzug_types = []

        for opponent in opponent_moves:
            board.push(opponent)
            eval_after = evaluate_position(engine, board)
            score_after = eval_after['score'].relative

            if abs(previous_score.score(mate_score=10000) - score_after.score(mate_score=10000)) > 50:
                zwischenzug_detected = True
                if board.is_check():
                    zwischenzug_types.append("Check")
                elif board.is_capture(opponent):
                    zwischenzug_types.append("Capture")
                elif board.gives_mate(opponent):
                    zwischenzug_types.append("Mate Threat")
                elif any(board.is_attacked_by(not board.turn, square) for square in board.legal_moves):
                    zwischenzug_types.append("Threatening to Capture")

            board.pop()

        if zwischenzug_detected:
            if current_turn == "White":
                white_zwischenzug_count += 1
                white_zwischenzug_types.extend(zwischenzug_types)
            else:
                black_zwischenzug_count += 1
                black_zwischenzug_types.extend(zwischenzug_types)

    white_zwischenzug_types = list(set(white_zwischenzug_types))
    black_zwischenzug_types = list(set(black_zwischenzug_types))

    return {
        "White zwischenzug count": white_zwischenzug_count,
        "White zwischenzug types": white_zwischenzug_types,
        "Black zwischenzug count": black_zwischenzug_count,
        "Black zwischenzug types": black_zwischenzug_types,
    }
