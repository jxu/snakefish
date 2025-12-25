"""Position class, as well as movegen"""

from move import *
from enum import IntEnum
from collections.abc import Iterator

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class Direction(IntEnum):
    N = 16
    E = 1
    S = -16
    W = -1
    NE = N + E
    SE = S + E
    SW = S + W
    NW = N + W

    # knight moves
    NNE = N + NE
    NNW = N + NW
    ENE = E + NE
    ESE = E + SE
    SSE = S + SE
    SSW = S + SW
    WNW = W + NW
    WSW = W + SW

Dir = Direction

PIECE_DIR = {
    PieceType.ROOK: (Dir.N, Dir.E, Dir.S, Dir.W),
    PieceType.BISHOP: (Dir.NE, Dir.SE, Dir.SW, Dir.NW),
    PieceType.KNIGHT: (Dir.NNE, Dir.NNW, Dir.ENE, Dir.ESE,
                       Dir.SSE, Dir.SSW, Dir.WNW, Dir.WSW)
}
PIECE_DIR[PT.QUEEN] = (
        PIECE_DIR[PT.ROOK] + PIECE_DIR[PT.BISHOP])
# king moves in the same directions as queen
PIECE_DIR[PT.KING] = PIECE_DIR[PT.QUEEN]


class Position:
    """Holds all information in a chess position.

    https://www.chessprogramming.org/Chess_Position

    Similar to FEN:
    - board: Piece placement as list of 128
    - side: Side to move (WHITE or BLACK)
    - castling: Castling rights (4 bools) (not if castling is actually possible)
    - ep_target: EP target square
    - halfmove: Halfmove clock
    - fullmove: Fullmove counter

    Also movegen methods are here for now.
    """

    def __init__(self, fen: str = START_FEN):
        """Constructs a Position from a given FEN string."""

        self.board: list[PieceCode] = [PC.EMPTY] * 128

        fen_split = fen.split()

        if len(fen_split) != 6:
            raise ValueError("Wrong number of FEN fields")
        
        piece_place = fen_split[0]  # board string

        # Parse piece placement string
        place_rank = piece_place.split('/')
        if len(place_rank) != 8:
            raise ValueError("Not 8 ranks")

        for i in range(8):
            row = 7 - i
            col = 0

            for c in place_rank[i]:
                if c.isdigit():
                    col += int(c)  # skip c spaces
                else:
                    is_black = c.islower()
                    c = c.upper()  # reduce piece checking cases

                    try:
                        # colored
                        piece = PieceCode(PIECETYPE_MAP[c])
                    except KeyError:
                        raise ValueError("Unrecognized piece")

                    # set negative if black
                    if is_black:
                        piece = invert_color(piece)
                    self.board[sq_index(row, col)] = piece

                    col += 1

            if col != 8:
                raise ValueError("Incorrect lengh row")

        # Parse the rest
        # Side to move
        if fen_split[1] == 'w':
            self.side = Color.WHITE
        elif fen_split[1] == 'b':
            self.side = Color.BLACK
        else:
            raise ValueError("invalid side")

        # Castling rights
        self.castling = [False] * 4
        castling = fen_split[2]
        if castling != '-':
            for c in castling:
                self.castling[CASTLE_MAP[c]] = True

        # EP target
        ep_target_raw = fen_split[3]

        if ep_target_raw == '-':
            self.ep_target = None
        elif is_coord_valid(ep_target_raw) and ep_target_raw[1] in "36":
            self.ep_target = sq_from_coord(ep_target_raw)
        else:
            raise ValueError("Invalid EP target")

        # Half move and full move counters
        self.halfmove = int(fen_split[4])
        self.fullmove = int(fen_split[5])


    def stepper_attacks(self, square: Square, piece_type: PieceType):
        """Generate targeted squares of pieces that don't depend on occupancy
        (king, knight)

        Bitboard style: Regardless of what is actually on square or
        what is occupying the targets!
        """
        if piece_type not in (PT.KNIGHT, PT.KING):
            raise ValueError

        directions = PIECE_DIR[piece_type]

        for direction in directions:
            step_square = square + direction
            if sq_valid(step_square):
                yield step_square


    # TODO: MAJOR OVERHAUL
    def generate_piece_attacks(self, side) -> Iterator[Move]:
        """Generate ALL (pseudo-legal) attacks by side

        Includes sliders (rook, bishop, queen) and steppers (king without castling, knight)
        """
        
        piece = self.board[orig_sq]
        piece_type = get_piece_type(piece)

        if piece_type == EMPTY:
            return

        # Generate no moves for not my side to move
        if get_color(piece) != self.side:
            return

        if piece_type == PAWN:
            yield from self.generate_pawn(orig_sq)
            return


        # piece is slider or stepper
        is_stepper = piece_type in (KING, KNIGHT)

        directions = PIECE_DIR[piece_type]
        
        for direction in directions:
            sq = orig_sq + direction  # start with one step already
            while sq_valid(sq):
                move = Move(orig_sq, sq)
                if self.board[sq] == EMPTY:
                    yield move
                    sq += direction

                    if is_stepper:
                        break

                # same color, end here
                elif get_color(self.board[sq]) == get_color(self.board[orig_sq]):
                    break
                else:  # enemy
                    yield move
                    break


    def generate_pawn(self, sq: int):
        """Generate psuedo-legal pawn movement"""
        piece = self.board[sq]
        assert get_piece_type(piece) == PAWN
        assert sq_row(sq) not in (0, 7)  # illegal pawn position

        # handle both colors at once

        direction = NN if get_color(piece) == WHITE else SS
        capture_dirs = (NE, NW) if get_color(piece) == WHITE else (SE, SW)
        home_row = 1 if get_color(piece) == WHITE else 6
        END_ROWS = (0, 7)
       
        # try single step, including possible promotion
        step_sq = sq + direction
        # sq_valid test not needed because pawn can't be in rows 0 or 7
        if self.board[step_sq] == EMPTY:
            # promotions
            if sq_row(step_sq) in END_ROWS:
                for promo in (KNIGHT, BISHOP, ROOK, QUEEN):
                    yield Move(sq, step_sq, promotion=promo)  # record promo
     
            else:
                yield Move(sq, step_sq)


        # try double step from home row if possible
        if sq_row(sq) == home_row:
            step2_sq = step_sq + direction
            # both squares in front must be empty
            if self.board[step_sq] == EMPTY and self.board[step2_sq] == EMPTY:
                yield Move(sq, step2_sq, double_pawn_push=True)

        # try capture (including en passant, based on position's target ep square)
        for dir in capture_dirs:
            capture_sq = sq + dir
            if sq_valid(capture_sq):
                capture_piece = self.board[capture_sq]
                if (capture_piece != EMPTY and 
                     get_color(piece) != get_color(capture_piece)):

                    # TODO: consolidate with previous promo yield
                    if sq_row(capture_sq) in END_ROWS:
                        for promo in (KNIGHT, BISHOP, ROOK, QUEEN):
                            yield Move(sq, capture_sq, promotion=promo)  # record promo
             
                    else:
                        yield Move(sq, capture_sq, capture=True)

                # EP capture
                if capture_sq == self.ep_target:
                    yield Move(sq, capture_sq, capture=True)



    def is_attacked(self, sq):
        """Determine if square (possibly empty) is attacked by enemy piece
        Enemy is determined by self's side

        (would be much more efficient with bitboards!)
        """
        assert sq_valid(sq)

        attacker_color = invert_color(self.side) 
       
        # loop through whole board
        for i in range(BOARD_SIZE):
            if not sq_valid(i): continue

            if get_color(self.board[i]) == attacker_color:
                attacks = self.generate_piece_attacks(i)
                for move in attacks:
                    if move.to == sq:
                        return True

        return False


    def generate_castle(self):
        """Generate possible castling moves (by side to move) in the position.

        To castle:
        - Must have castling rights (tracked seperately by Position object)
        - Must have empty spaces in between
        - Cannot castle out of, through, or into check
          - Not included even for pseudo-legal
        """

        # arrays in order of WK, WQ, BK, BQ
        KING_SQUARES = [(E1, F1, G1), (E1, D1, C1), (E8, F8, G8), (E8, D8, C8)]

        IN_BETWEEN = [(F1, G1), (D1, C1, B1), (F8, G8), (D8, C8, B8)]
        KING_COLOR = (WHITE, WHITE, BLACK, BLACK)

        for i in range(4):
            # only generate moves for side to move
            if KING_COLOR[i] != self.side:
                continue

            # castling rights
            if self.castling[i]:
                assert get_piece_type(self.board[KING_SQUARES[i][0]]) == KING
                # squares empty
                if all(self.board[s] == EMPTY for s in IN_BETWEEN[i]):
                    # king not in check
                    if all(not self.is_attacked(s) for s in KING_SQUARES[i]):
                        yield Move(KING_SQUARES[i][0], KING_SQUARES[i][-1], castle=True)
                    

    def make_move(self, move: Move):
        """Make pseudo-legal move, updating Position flags

        See https://www.chessprogramming.org/Forsyth-Edwards_Notation
        for how position is stored
        """
        
        # ensure to square doesn't have piece of same color
        assert get_color(self.board[move.to]) != self.side

        # piece to move
        piece = self.board[move.from_]
        # piece should be side to move color
        assert get_color(piece) == self.side

        # do board update: from square is vacated, to square is replaced
        self.board[move.from_] = EMPTY
        self.board[move.to] = piece


        # castling rights are based on if kings and rooks have moved
        # (left their from square) or been captured

        # TODO: make more robust without assuming indices WK, WQ, BK, BQ
        ROOK_SQUARE = (H1, A1, H8, A8)
        ROOK_PIECE  = (ROOK, ROOK, -ROOK, -ROOK)
        KING_SQUARE = (E1, E1, E8, E8)
        KING_PIECE  = (KING, KING, -KING, -KING)

        for i in range(4):
            if (self.board[ROOK_SQUARE[i]] != ROOK_PIECE[i] or 
                    self.board[KING_SQUARE[i]] != KING_PIECE[i]):
                self.castling[i] = False

        # EP target set always if double pawn push (assume valid)
        if move.double_pawn_push:
            row = sq_row(move.to)
            # EP is set behind to_square
            new_row = row - 1 if get_color(piece) == WHITE else row + 1 
            self.ep_target = sq_index(new_row, sq_col(move.to))
        else:
            self.ep_target = None

        # Halfmove clock reset to zero after a capture or pawn move,
        # increment otherwise
        if move.capture or get_piece_type(piece) == PAWN:
            self.halfmove = 0
        else:
            self.halfmove += 1

        # Fullmove counter increments on black's move
        if self.side == BLACK:
            self.fullmove += 1

        # finally, invert side to move
        self.side = invert_color(self.side)
