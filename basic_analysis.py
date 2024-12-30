import chess

def analyze_game(game, engine, eco_database):
    results = {}

    # Temel bilgiler
    results['White'] = game.headers.get("White", "Unknown")
    results['Black'] = game.headers.get("Black", "Unknown")
    results['WhiteElo'] = game.headers.get("WhiteElo", "Unknown")
    results['BlackElo'] = game.headers.get("BlackElo", "Unknown")
    results['Result'] = game.headers.get("Result", "Unknown")

    # Tahta ve hamleler
    board = game.board()
    move_count = 0
    white_castled = "Not Castled"
    black_castled = "Not Castled"

    for move in game.mainline_moves():
        move_count += 1

        if board.is_kingside_castling(move):
            if board.turn:
                white_castled = "Short"
            else:
                black_castled = "Short"
        elif board.is_queenside_castling(move):
            if board.turn:
                white_castled = "Long"
            else:
                black_castled = "Long"

        board.push(move)

    results['WhiteCastling'] = white_castled
    results['BlackCastling'] = black_castled
    results['TotalMoves'] = move_count // 2

    # ECO bilgisi
    from eco_utils import get_opening_name_and_code
    eco_code, opening_name = get_opening_name_and_code(board, eco_database)
    results['OpeningName'] = opening_name
    results['ECOCode'] = eco_code

    # Sonuç analizi
    result = game.headers.get("Result", "Unknown")
    if result == "1/2-1/2": 
        # Check type of draw
        if board.is_stalemate():
            draw_type = "Stalemate"
        elif board.is_repetition():
            draw_type = "Threefold Repetition"
        elif board.is_insufficient_material():
            draw_type = "Insufficient Material"
        else:
            draw_type = "Agreement (Anlaşmalı Berabere)"

        results['DrawType'] = draw_type
    
    if result in ["1-0", "0-1"]:
        evaluation = engine.analyse(board, chess.engine.Limit(time=1))
        score = evaluation['score'].relative
        last_move = board.pop()
        if board.is_checkmate():
            winning_method = "Checkmate"
        else:
            winning_method = "Resignation"
        board.push(last_move)  
        results['WinningMethod'] = winning_method
        if score.is_mate():
            mate_distance = score.mate()
            if not board.turn:
                mate_distance *= -1

            if (result == "1-0" and mate_distance < 0 ) or (result == "0-1" and mate_distance > 0):
                results['ResignationAnalysis'] = "Incorrect, resigning side had a forced mate."
            elif (result == "1-0" and mate_distance > 0) or (result == "0-1" and mate_distance < 0):
                results['ResignationAnalysis'] = "Correct, opponent has a forced mate."
            else:
                results['ResignationAnalysis'] = "Inconsistent evaluation."
        else:
            results['ResignationAnalysis'] = "Evaluation does not detect a forced mate."

    return results
