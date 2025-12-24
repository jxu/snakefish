from board import *

def test_get_color():
    assert get_color(PieceCode.BKING) == Color.BLACK
    assert get_color(PieceCode.WKNIGHT) == Color.WHITE
    assert get_color(PieceCode.EMPTY) == Color.NEUTRAL


def test_get_piece_type():
    assert get_piece_type(PieceCode.BKING) == PieceType.KING
    assert get_piece_type(PieceCode.WKNIGHT) == PieceType.KNIGHT


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



