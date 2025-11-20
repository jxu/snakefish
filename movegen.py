from move import *
from collections.abc import Iterator

NN = 16
EE = 1
SS = -16
WW = -1
NE = NN + EE
SE = SS + EE
SW = SS + WW
NW = NN + WW

def generate_rook_moves(pos: Position, sq: int) -> Iterator[Move]:
    """Generate pseudo-legal rook moves from pos and board"""
    orig_sq = sq
    
    for direction in (NN, EE, SS, WW):
        sq = orig_sq + direction  # start with one step already
        while sq_valid(sq):
            move = Move(orig_sq, sq)
            if pos.board[sq] == EMPTY:
                yield move
                sq += direction

            # same color, end here
            elif get_color(pos.board[sq]) == get_color(pos.board[orig_sq]):
                break
            else:  # enemy
                yield move
                break

