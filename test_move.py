from move import *

def test_move_uci():
    assert Move(Square.A1, Square.C2).uci() == "a1c2"
    assert Move(Square.E7, Square.E8,
                promotion=PieceType.QUEEN).uci() == "e7e8q"
