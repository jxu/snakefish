from board import *

PROMO_MAP = {
    KNIGHT: 'n',
    BISHOP: 'b',
    ROOK: 'r',
    QUEEN: 'q',
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
    def __init__(self, from_sq, to_sq, capture=False, promotion=EMPTY,
                 double_pawn_push=False, castle=False):
        assert sq_valid(from_sq)
        assert sq_valid(to_sq)
        assert from_sq != to_sq  # null move

        self.from_ = from_sq
        self.to = to_sq
        self.capture = capture
        self.promotion = promotion
        self.double_pawn_push = double_pawn_push
        self.castle = castle

    def __str__(self):
        """Return pure algebraic coordinate notation, like h7h8q"""

        s = sq_to_coord(self.from_) + sq_to_coord(self.to)
        if self.promotion:
            s += PROMO_MAP[self.promotion]

        return s


