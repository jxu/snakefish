from move import *


def test_move_str():
    assert str(Move(SQ("a1"), SQ("c2"))) == "a1c2"
    assert str(Move(SQ("e7"), SQ("e8"), promotion=QUEEN)) == "e7e8q"
