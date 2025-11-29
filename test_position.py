from position import *

def test_position():
    start_pos = Position(START_FEN)


    # Starting board by increasing row (upside down)
    BOARD = [
        [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK],
        [PAWN]*8,
        [EMPTY]*8,
        [EMPTY]*8,
        [EMPTY]*8,
        [EMPTY]*8,
        [-PAWN,]*8,
        [-ROOK,-KNIGHT,-BISHOP,-QUEEN,-KING,-BISHOP,-KNIGHT,-ROOK],
    ]

    for r in range(8):
        for c in range(8):
            assert start_pos.board[sq_index(r, c)] == BOARD[r][c]

    assert start_pos.side == WHITE
    assert start_pos.castling == [True]*4
    assert start_pos.ep_target == None
    assert start_pos.halfmove == 0
    assert start_pos.fullmove == 1

    # Check position by black's move with EP square
    fen_1e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

    # modify start board
    BOARD[3][4] = PAWN
    BOARD[1][4] = EMPTY

    pos1 = Position(fen_1e4)

    for r in range(8):
        for c in range(8):
            assert pos1.board[sq_index(r, c)] == BOARD[r][c]


    assert pos1.side == BLACK
    assert pos1.castling == [True]*4
    assert pos1.ep_target == sq_from_coord("e3")
    assert pos1.halfmove == 0
    assert pos1.fullmove == 1



def moves_as_str(moves):
    """Return moveslist as list of algebraic UCI move strings"""
    return sorted([str(m) for m in moves])


def test_rook():
    pos = Position("8/2K5/8/2R2P2/8/8/2r5/2k5 w - - 0 1")
    moves = pos.generate_attacks(SQ("c5"))  # c5 white rook

    assert (moves_as_str(moves) == 
        ['c5a5', 'c5b5', 'c5c2', 'c5c3', 'c5c4', 'c5c6', 'c5d5', 'c5e5'])

    # no white moves for black rook
    assert list(pos.generate_attacks(SQ("c2"))) == []

    # no white moves for empty
    assert list(pos.generate_attacks(SQ("a1"))) == [] 

    # switch to black turn
    pos.side = BLACK
    moves = pos.generate_attacks(SQ("c2"))  # c2 black rook
    assert (moves_as_str(moves) == 
            ['c2a2', 'c2b2', 'c2c3', 'c2c4', 'c2c5', 'c2d2', 'c2e2', 'c2f2', 'c2g2', 'c2h2'])

    start_pos = Position(START_FEN)
    assert (moves_as_str(start_pos.generate_attacks(SQ("a1"))) == [])


def test_bishop():
    pos = Position("8/4P3/8/2Bk4/2b5/8/5p2/5K2 w - - 0 1")
    moves = pos.generate_attacks(SQ("c5"))  # white bishop
    assert (moves_as_str(moves) == 
            ['c5a3', 'c5a7', 'c5b4', 'c5b6', 'c5d4', 'c5d6', 'c5e3', 'c5f2'])

    pos.side = BLACK
    moves = pos.generate_attacks(SQ("c4"))  # black bishop
    assert (moves_as_str(moves) == 
            ['c4a2', 'c4a6', 'c4b3', 'c4b5', 'c4d3', 'c4e2', 'c4f1'])

    moves = Position(START_FEN).generate_attacks(SQ("c1"))
    assert list(moves) == []


def test_queen():
    pos = Position("8/8/8/3Q4/8/8/8/8 w - - 0 1")
    moves = pos.generate_attacks(SQ("d5"))
    assert len(list(moves)) == 27

def test_king_step():
    # doesn't include castling!
    pos = Position("8/8/8/3K4/6k1/8/8/8 w - - 0 1")
    moves = pos.generate_attacks(SQ("d5"))
    assert (moves_as_str(moves) ==
            ['d5c4', 'd5c5', 'd5c6', 'd5d4', 'd5d6', 'd5e4', 'd5e5', 'd5e6'])
    
def test_knight():
    pos = Position("8/8/8/3N4/8/8/8/8 w - - 0 1")
    moves = pos.generate_attacks(SQ("d5"))
    assert (moves_as_str(moves) == 
        ['d5b4', 'd5b6', 'd5c3', 'd5c7', 'd5e3', 'd5e7', 'd5f4', 'd5f6'])


def test_pawn():
    pos = Position("1k3b2/6P1/8/4pPpP/3p4/1P2N3/1PPP4/1K6 w - e6 0 1")
    assert moves_as_str(pos.generate_attacks(SQ("c2"))) == ["c2c3", "c2c4"]
    assert moves_as_str(pos.generate_attacks(SQ("b2"))) == []


    assert moves_as_str(pos.generate_attacks(SQ("d2"))) == ["d2d3"]
    # e.p.
    assert moves_as_str(pos.generate_attacks(SQ("f5"))) == ["f5e6", "f5f6"]
    assert moves_as_str(pos.generate_attacks(SQ("h5"))) == ["h5h6"]


    # promotions
    assert moves_as_str(pos.generate_attacks(SQ("g7"))) == \
        ["g7f8b", "g7f8n", "g7f8q", "g7f8r",
    "g7g8b", "g7g8n", "g7g8q", "g7g8r"]
         
    # black pawn
    pos.side = BLACK
    assert moves_as_str(pos.generate_attacks(SQ("d4"))) == ["d4d3", "d4e3"]


def test_is_attacked():
    # Test only for castling
    pos = Position("r3kN1r/1K6/8/8/2B1R3/8/8/8 b kq - 0 1")

    assert not pos.is_attacked(SQ("f8"), WHITE)  # occupied but not attacked
    assert pos.is_attacked(SQ("e8"), WHITE)  # king in check
    assert pos.is_attacked(SQ("g8"), WHITE)
    assert pos.is_attacked(SQ("b8"), WHITE)
    assert pos.is_attacked(SQ("c8"), WHITE)
    assert not pos.is_attacked(SQ("d8"), WHITE)


def test_castle():
    # starting position
    pos = Position(START_FEN)
    assert list(pos.generate_castle()) == []


    # all castling position
    pos = Position("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    
    moves = pos.generate_castle() 
    assert moves_as_str(moves) == ["e1c1", "e1g1", "e8c8", "e8g8"]
