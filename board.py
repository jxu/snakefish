"""Piece and board definitions.

0x88 board
https://www.chessprogramming.org/0x88

128-byte array stores the board. Half of the board are normal squares.
the other half of the board is garbage, for boundary checking
the (0-indexed) row and col are indexed in binary as 0rrr0fff
Note that square a1 is 0x00

  a  b  c  d  e  f  g  h < file
8 70 71 72 73 74 75 76 77|78 79 7A 7B 7C 7D 7E 7F
7 60 61 62 63 64 65 66 67|68 69 6A 6B 6C 6D 6E 6F
6 50 51 52 53 54 55 56 57|58 59 5A 5B 5C 5D 5E 5F
5 40 41 42 43 44 45 46 47|48 49 4A 4B 4C 4D 4E 4F
4 30 31 32 33 34 35 36 37|38 39 3A 3B 3C 3D 3E 3F
3 20 21 22 23 24 25 26 27|28 29 2A 2B 2C 2D 2E 2F
2 10 11 12 13 14 15 16 17|18 19 1A 1B 1C 1D 1E 1F
1 00 01 02 03 04 05 06 07|08 09 0A 0B 0C 0D 0E 0F
^ rank

A square is represented by an index into a 128 entry 0x88 board
Uses an int instead of object for efficiency

Square Coordinates are file-rank combo like h8
"""

BOARD_SIZE = 128

# global constant squares for convenience
A1, B1, C1, D1, E1, F1, G1, H1 = range(0x00, 0x08)
A2, B2, C2, D2, E2, F2, G2, H2 = range(0x10, 0x18)
A3, B3, C3, D3, E3, F3, G3, H3 = range(0x20, 0x28)
A4, B4, C4, D4, E4, F4, G4, H4 = range(0x30, 0x38)
A5, B5, C5, D5, E5, F5, G5, H5 = range(0x40, 0x48)
A6, B6, C6, D6, E6, F6, G6, H6 = range(0x50, 0x58)
A7, B7, C7, D7, E7, F7, G7, H7 = range(0x60, 0x68)
A8, B8, C8, D8, E8, F8, G8, H8 = range(0x70, 0x78)

# Piece type (positive for white, negative for black)
EMPTY   = 0
PAWN    = 1
KNIGHT  = 2
BISHOP  = 3
ROOK    = 4
QUEEN   = 5
KING    = 6


PIECE_MAP = {
    'P': PAWN,
    'N': KNIGHT,
    'B': BISHOP,
    'R': ROOK,
    'Q': QUEEN,
    'K': KING,
}

# color enum
BLACK = -1
WHITE = 1
NEUTRAL = 0

# castling flags
CASTLE_WK = 0
CASTLE_WQ = 1
CASTLE_BK = 2
CASTLE_BQ = 3

CASTLE_MAP = {
    'K': CASTLE_WK,
    'Q': CASTLE_WQ,
    'k': CASTLE_BK,
    'q': CASTLE_BQ,
}


def get_color(piece):
    if piece > 0: return WHITE
    if piece < 0: return BLACK
    return NEUTRAL


def invert(color):
    assert color != NEUTRAL
    return -color


def get_type(piece):
    return abs(piece)

# 0x88 board coordinate transformations

def sq_index(row, col):
    assert 0 <= row <= 7 and 0 <= col <= 7
    return 16 * row + col


def sq_valid(sq):
    """Check if sq is a valid 0x88 square."""
    return (sq & 0x88) == 0  # the magic


def sq_col(sq):
    """Get square's column 0-7 (corresponds to files a-h)"""
    return sq & 0x7  # low nibble


def sq_row(sq):
    """Get square's row 0-7 (corresponds to ranks 1-8)"""
    return sq >> 4  # high nibble


def sq_to_coord(sq: int) -> str:
    """Get algebraic coordinates from square index."""
    assert sq_valid(sq)
    file = "abcdefgh"[sq_col(sq)]
    row = str(sq_row(sq) + 1)
    return file + row


def sq_from_coord(coord: str) -> int:
    """Get square index from algebraic coordinates."""
    assert is_coord_valid(coord)
    col = ord(coord[0]) - ord('a')
    row = ord(coord[1]) - ord('1')
    return sq_index(row, col)
   
# shortcut function
SQ = sq_from_coord

def is_coord_valid(coord: str) -> bool:
    """Check if a string is a valid algebraic coordinate."""
    return ((len(coord) == 2) and
            (coord[0] in "abcdefgh") and 
            (coord[1] in "12345678"))

