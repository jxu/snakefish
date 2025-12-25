from board import *

# used for writing promotions in UCI notation
PROMO_LETTER = {
    PieceType.KNIGHT: 'n',
    PieceType.BISHOP: 'b',
    PieceType.ROOK: 'r',
    PieceType.QUEEN: 'q',
}


class Move:
    """Encode move with from square, to square, and flags.

    https://www.chessprogramming.org/Encoding_Moves

    - from_: square
    - to: square
    
    flags
    - capture: bool
    - promotion: PieceType
    - double_pawn_push: bool, used to set ep target
    - castle: bool
    """
    def __init__(
            self,
            from_sq: Square,
            to_sq: Square,
            capture=False,
            promotion=PieceType.EMPTY,
            double_pawn_push=False,
            castle=False):
        # Sanity checks
        assert sq_valid(from_sq)
        assert sq_valid(to_sq)
        assert from_sq != to_sq  # null move

        self.from_ = from_sq
        self.to = to_sq
        self.capture = capture
        self.promotion = promotion
        self.double_pawn_push = double_pawn_push
        self.castle = castle

    def uci(self):
        """Return UCI pure algebraic coordinate notation, like h7h8q"""

        s = sq_to_coord(self.from_) + sq_to_coord(self.to)
        if self.promotion:
            s += PROMO_LETTER[self.promotion]

        return s
