from move import *


def test_move_str():
    assert str(Move(sq_from_coord("a1"), sq_from_coord("c2"))) == "a1c2"
