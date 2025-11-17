from board import *

def test_get_color():
    assert get_color(-KING) == BLACK
    assert get_color(KNIGHT) == WHITE
    assert get_color(EMPTY) == NEUTRAL

def test_sq_index():
    assert sq_index(1, 2) == 0x12

def test_sq_valid():
    assert sq_valid(0x00)
    assert sq_valid(0x77)
    assert not sq_valid(0x80)


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


    # Starting board by increasing row (upside down)
    BOARD = [
        [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK],
        [PAWN]*8,
        *[[EMPTY]*8 for _ in range(4)],  # independent rows
        [-PAWN,]*8,
        [-ROOK,-KNIGHT,-BISHOP,-QUEEN,-KING,-BISHOP,-KNIGHT,-ROOK],
    ]

    for r in range(8):
        for c in range(8):
            assert start_pos.board[sq_index(r, c)] == BOARD[r][c]

    assert start_pos.black_move == False
    assert start_pos.castling == "KQkq"
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


    assert pos1.black_move == True
    assert pos1.castling == "KQkq"
    assert pos1.ep_target == sq_from_coord("e3")
    assert pos1.halfmove == 0
    assert pos1.fullmove == 1


