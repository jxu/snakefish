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
    """
    def __init__(self, from_ind, to_ind, capture=False, promotion=EMPTY):
        assert sq_valid(from_ind)
        assert sq_valid(to_ind)
        assert from_ind != to_ind  # null move

        self.from_ = from_ind
        self.to = to_ind
        self.capture = capture
        self.promotion = promotion

    def __str__(self):
        """Return pure algebraic coordinate notation, like h7h8q"""

        s = sq_to_coord(self.from_) + sq_to_coord(self.to)
        if self.promotion:
            s += PROMO_MAP[self.promotion]

        return s


