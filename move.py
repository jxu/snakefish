from board import *

class Move:
    """Encode move with from square, to square, and flags.

    https://www.chessprogramming.org/Encoding_Moves
    """
    def __init__(self, from_ind, to_ind, flags=0):
        assert sq_valid(from_ind)
        assert sq_valid(to_ind)
        assert from_ind != to_ind  # null move

        self.from_ = from_ind
        self.to = to_ind
        self.flags = flags  # TODO


    def __str__(self):
        """Return pure algebraic coordinate notation, like h7h8q"""

        # TODO: implement promotions
        if self.flags:
            raise NotImplementedError

        return sq_to_coord(self.from_) + sq_to_coord(self.to)


