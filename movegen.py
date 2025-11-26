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

DIRECTION_ROOK = (NN, EE, SS, WW)
DIRECTION_BISHOP = (NE, SE, SW, NW)
DIRECTION_QUEEN = DIRECTION_ROOK + DIRECTION_BISHOP

DIRECTION_KING = DIRECTION_QUEEN
DIRECTION_KNIGHT = (NN+NE, NN+NW, EE+NE, EE+SE, SS+SE, SS+SW, WW+SW, WW+NW)

def generate_slider(directions: tuple, pos: Position, orig_sq: int) -> Iterator[Move]:
    """Generate pseudo-legal slider moves from starting pos and board"""
    
    for direction in directions:
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

def generate_stepper(directions, pos, orig_sq):
    """Generate psuedo-legal moves for pieces that have fixed movement"""
    
    piece_type = get_type(pos.board[orig_sq])
    assert piece_type in (KING, KNIGHT)

    for direction in directions:
        sq = orig_sq + direction
        if sq_valid(sq):
            move = Move(orig_sq, sq)
            if pos.board[sq] == EMPTY:
                yield move
            elif get_color(pos.board[sq]) != get_color(pos.board[orig_sq]):
                yield move
