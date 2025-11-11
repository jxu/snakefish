from board import *

def test_is_piece_black():
    assert is_piece_black(-KING)
    assert not is_piece_black(KNIGHT)
    assert not is_piece_black(EMPTY)

def test_sq_index():
    assert sq_index(1, 2) == 0x12

def test_sq_valid():
    assert sq_valid(0x00)
    assert sq_valid(0x77)
    assert not sq_valid(0x80)
    assert not sq_valid(-1)  # maybe not necessary


def test_sq_col():
    assert sq_col(0x54) == 4


def test_sq_row():
    assert sq_row(0x54) == 5


def test_sq_to_coord():
    assert sq_to_coord(0x00) == "a1"
    assert sq_to_coord(0x57) == "h6"


def test_sq_from_coord():
    assert sq_from_coord("a1") == 0x00
    assert sq_from_coord("h6") == 0x57


def test_is_coord_valid():
    assert not is_coord_valid("")
    assert not is_coord_valid("a0")
    assert is_coord_valid("b2")


def test_position():
    start_pos = Position(START_FEN)

    row0 = (ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK)

    for r in range(8):
        for f in range(8):
            piece = start_pos.board[sq_index(r, f)]
            if r == 0:  # white pieces
                assert piece == row0[f]
            elif r == 1:  # white pawns
                assert piece == PAWN
            elif r == 6:  # black pawns
                assert piece == -PAWN
            elif r == 7:  # black pieces
                assert piece == -row0[f]
            else:
                assert piece == EMPTY

    assert start_pos.black_move == False
    assert start_pos.castling == "KQkq"
    assert start_pos.ep_target == None
    assert start_pos.halfmove == 0
    assert start_pos.fullmove == 1

    fen_1e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

    pos1 = Position(fen_1e4)
    assert pos1.black_move == True
    assert pos1.castling == "KQkq"
    assert pos1.ep_target == sq_from_coord("e3")
    assert pos1.halfmove == 0
    assert pos1.fullmove == 1


