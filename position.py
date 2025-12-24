"""Position class, as well as movegen"""

from board import *
from move import *
from collections.abc import Iterator

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


NN = 16
EE = 1
SS = -16
WW = -1
NE = NN + EE
SE = SS + EE
SW = SS + WW
NW = NN + WW

DIRECTIONS = {
    ROOK: (NN, EE, SS, WW),
    BISHOP: (NE, SE, SW, NW),
    KNIGHT: (NN+NE, NN+NW, EE+NE, EE+SE, SS+SE, SS+SW, WW+SW, WW+NW)
}
DIRECTIONS[QUEEN] = DIRECTIONS[ROOK] + DIRECTIONS[BISHOP]
DIRECTIONS[KING] = DIRECTIONS[QUEEN]


class Position:
    """Holds all information in a chess position.

    https://www.chessprogramming.org/Chess_Position

    Similar to FEN:
    - board: Piece placement as list of 128
    - side: Side to move (WHITE or BLACK)
    - castling: Castling rights (4 bools) 
        (not if castling is actually possible)
    - ep_target: EP target square
    - halfmove: Halfmove clock
    - fullmove: Fullmove counter

    Also movegen methods are here for now.
    """

    def __init__(self, fen):
        """Constructs a Position from a given FEN string."""

        self.board = [EMPTY] * 128

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
                        piece = PIECE_MAP[c]
                    except KeyError:
                        raise ValueError("Unrecognized piece")

                    # set negative if black
                    if is_black:
                        piece = -piece
                    self.board[sq_index(row, col)] = piece

                    col += 1

            if col != 8:
                raise ValueError("Incorrect lengh row")

        # Parse the rest
        # Side to move
        if fen_split[1] == 'w':
            self.side = WHITE
        elif fen_split[1] == 'b':
            self.side = BLACK
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



    def generate_attacks(self, orig_sq: int) -> Iterator[Move]:
        """Generate pseudo-legal piece moves from the position's board

        Detect the piece and color from given square.

        Includes sliders (rook, bishop, queen) and steppers (king without castling, knight)

        castling handled separately
        """
        
        piece = self.board[orig_sq]
        piece_type = get_type(piece)

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

        directions = DIRECTIONS[piece_type]
        
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
        assert get_type(piece) == PAWN
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



    def is_attacked(self, sq, attacker_color):
        """Determine if square (possibly empty) is attacked by piece with given color

        would be much more efficient with bitboards
        """
        # ignore current side to move, generate attacks by attacker_color
        orig_side = self.side
        self.side = attacker_color
        
        for i in range(BOARD_SIZE):
            if not sq_valid(i): continue

            if get_color(self.board[i]) == attacker_color:
                attacks = self.generate_attacks(i)
                for move in attacks:
                    if move.to == sq:
                        self.side = orig_side  # restore
                        return True

        self.side = orig_side  # restore
        return False


    def generate_castle(self):
        """Generate possible castling moves (by side to move) in the position.

        To castle:
        - Must have castling rights (tracked seperately by Position object)
        - Must have empty spaces in between
        - Cannot castle out of, through, or into check
          - (Technically ending in check is pseudolegal)
        """

        # arrays in order of WK, WQ, BK, BQ
        KING_SQUARES = [(E1, F1, G1), (E1, D1, C1), (E8, F8, G8), (E8, D8, C8)]

        IN_BETWEEN = [(F1, G1), (D1, C1, B1), (F8, G8), (D8, C8, B8)]
        KING_COLOR = (WHITE, WHITE, BLACK, BLACK)
        ENEMY_COLOR = (BLACK, BLACK, WHITE, WHITE)

        for i in range(4):
            # only generate moves for side to move
            if KING_COLOR[i] != self.side:
                continue

            # castling rights
            if self.castling[i]:
                assert get_type(self.board[KING_SQUARES[i][0]]) == KING
                # squares empty
                if all(self.board[s] == EMPTY for s in IN_BETWEEN[i]):
                    # king not in check
                    if all(not self.is_attacked(s, ENEMY_COLOR[i]) for s in KING_SQUARES[i]):
                        yield Move(KING_SQUARES[i][0], KING_SQUARES[i][-1], castle=True)
                    

    def make_move(self, move: Move):
        """Make pseudo-legal move, updating Position flags"""
        
        # ensure to square doesn't have piece of same color
        assert get_color(self.board[move.to]) != self.side

        # piece to move
        piece = self.board[move.from_]
        # piece should be side to move color
        assert get_color(piece) == self.side

        # do board update: from square is vacated, to square is replaced
        self.board[move.from_] = EMPTY
        self.board[move.to] = piece
        
        # invert side to move
        self.side = invert(self.side)

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

        # EP target set always if double pawn push
