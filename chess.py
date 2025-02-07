# Piece definitions (negative for black)
EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

PIECE_MAP = {'P': PAWN, 'N': KNIGHT, 'B': BISHOP, 'R': ROOK,
             'Q': QUEEN, 'K': KING}


# 0x88 board coordinate transformations (all 0-indexed)
# rank index 0-7 encodes ranks 1-8
# file index 0-7 encodes files a-h
def sqind(rank07, file07):
    return 16 * rank07 + file07


def sqrank(ind):
    return ind & 0x7


def sqfile(ind):
    assert (ind >> 4) < 8
    return ind >> 4


class Position:
    """Holds all information to set up a chess position, like FEN.

    0x88 board
    the other half of the board is garbage, for boundary checking
    the 0-indexed rank and file are indexed as 0b0rrr0fff

       a  b  c  d  e  f  g  h
    8 70 71 72 73 74 75 76 77|78 79 7A 7B 7C 7D 7E 7F
    7 60 61 ...              |
    6 50                     |
    5 40                     |
    4 30                     |
    3 20                     |
    2 10                     |
    1 00                     |

    """

    def __init__(self, fen):
        self.board = [EMPTY] * 128


        piece_place, side, castling, ep_target, halfmove, movecounter = \
            fen.split()

        place_rank = piece_place.split('/')
        if len(place_rank) != 8:
            raise ValueError("Not 8 ranks")

        for i in range(8):
            rank = 7 - i
            file = 0

            for c in place_rank[i]:
                if c.isdigit():
                    file += int(c)  # skip c spaces
                else:
                    is_black = c.islower()
                    c = c.upper()  # reduce piece checking cases

                    try:
                        piece = PIECE_MAP[c]
                    except KeyError:
                        raise ValueError("Unrecognized piece")

                    # set negative if black
                    if is_black:
                        piece = -piece
                    self.board[sqind(rank, file)] = piece

                    file += 1


            if file != 8:
                raise ValueError("Incorrect rank placement")



def test_fen():
    start_pos = \
        Position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    rank0 = (ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK)

    for r in range(8):
        for f in range(8):
            piece = start_pos.board[sqind(r,f)]
            if r == 0:
                assert piece == rank0[f]
            elif r == 1:
                assert piece == PAWN
            elif r == 6:
                assert piece == -PAWN
            elif r == 7:
                assert piece == -rank0[f]
            else:
                assert piece == EMPTY
