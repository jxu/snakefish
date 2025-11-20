from movegen import *

def moves_as_str(moves):
    """Return moveslist as list of algebraic UCI move strings"""
    return sorted([str(m) for m in moves])


def test_rook():
    pos = Position("8/2K5/8/2R2P2/8/8/2r5/2k5 w - - 0 1")
    moves = generate_rook_moves(pos, SQ("c5"))  # c5 white rook

    assert (moves_as_str(moves) == 
        ['c5a5', 'c5b5', 'c5c2', 'c5c3', 'c5c4', 'c5c6', 'c5d5', 'c5e5'])

    moves = generate_rook_moves(pos, SQ("c2"))  # c2 black rook
    assert (moves_as_str(moves) == 
            ['c2a2', 'c2b2', 'c2c3', 'c2c4', 'c2c5', 'c2d2', 'c2e2', 'c2f2', 'c2g2', 'c2h2'])

    start_pos = Position(START_FEN)
    assert (moves_as_str(generate_rook_moves(start_pos, SQ("a1"))) == [])

