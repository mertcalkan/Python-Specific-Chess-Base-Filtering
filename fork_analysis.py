import chess
import chess.pgn

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: float('inf')  # Kralın kaybı oyunun sonudur
}

def detect_fork(board, move):
    """
    Bir hamlenin çatal oluşturup oluşturmadığını değerlendirir.
    - Çatal, bir taşın aynı anda iki veya daha fazla değerli taşı tehdit etmesidir.
    """
    attacker_square = move.to_square
    attacker_piece = board.piece_at(attacker_square)

    if not attacker_piece:
        return None

    # Tehdit edilen kareleri kontrol et
    attacked_squares = board.attacks(attacker_square)
    targets = []

    for square in attacked_squares:
        target_piece = board.piece_at(square)
        if target_piece and target_piece.color != attacker_piece.color:
            # Değerli bir taşı tehdit ediyor
            targets.append((square, target_piece.symbol(), PIECE_VALUES[target_piece.piece_type]))

    # Çatal durumunu değerlendir
    if len(targets) >= 2:
        # Değerli taşları kontrol et ve savunma durumu analiz et
        valuable_targets = [target for target in targets if target[2] > PIECE_VALUES[attacker_piece.piece_type]]
        if len(valuable_targets) >= 2:
            return {
                "attacker": attacker_piece.symbol(),
                "targets": valuable_targets
            }
    return None


def analyze_forks(game):
    """
    Bir oyundaki çatal durumlarını analiz eder.
    - Beyaz ve siyah için çatal sayısını döner.
    """
    board = game.board()
    white_fork_count = 0
    black_fork_count = 0
    white_fork_details = []
    black_fork_details = []

    for move in game.mainline_moves():
        # Hamleyi uygula
        board.push(move)
        fork = detect_fork(board, move)

        if fork:
            if board.turn:  # Eğer sıra beyazda ise, önceki hamle siyahtan gelmiştir
                black_fork_count += 1
                black_fork_details.append(fork)
            else:
                white_fork_count += 1
                white_fork_details.append(fork)

    return {
        "White fork count": white_fork_count,
        "White fork details": white_fork_details if white_fork_count > 0 else None,
        "Black fork count": black_fork_count,
        "Black fork details": black_fork_details if black_fork_count > 0 else None,
    }