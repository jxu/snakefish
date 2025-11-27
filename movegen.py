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


def generate_pawn(pos: Position, sq: int):
    """Generate psuedo-legal pawn movement"""
    piece = pos.board[sq]
    assert get_type(piece) == PAWN
    assert sq_row(sq) not in (0, 7)  # illegal pawn position

    # handle both colors at once
    to_sqs = []

    direction = NN if get_color(piece) == WHITE else SS
    capture_dirs = (NE, NW) if get_color(piece) == WHITE else (SE, SW)
    home_row = 1 if get_color(piece) == WHITE else 6
   
    # try single step, including possible promotion
    step_sq = sq + direction
    # sq_valid test not needed because pawn can't be in rows 0 or 7
    if pos.board[step_sq] == EMPTY:
        to_sqs.append(step_sq)


    # try double step if possible
    if sq_row(sq) == home_row:
        step2_sq = step_sq + direction
        # both squares in front must be empty
        if pos.board[step_sq] == EMPTY and pos.board[step2_sq] == EMPTY:
            to_sqs.append(step2_sq)

    # try capture (including en passant, based on position's target ep square)
    for dir in capture_dirs:
        capture_sq = sq + dir
        if sq_valid(capture_sq):
            capture_piece = pos.board[capture_sq]
            if ((capture_piece != EMPTY and get_color(piece) != get_color(capture_piece)) or
                    capture_sq == pos.ep_target):
                to_sqs.append(capture_sq)

    # Generate moves, possibly with promotions
    for to_sq in to_sqs:
        if sq_row(to_sq) in (0, 7):
            for promo in (KNIGHT, BISHOP, ROOK, QUEEN):
                yield Move(sq, to_sq, promotion=promo)
        else:
            yield Move(sq, to_sq)
