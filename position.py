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
    - Piece placement
    - Side to move
    - Castling rights
    - EP target square
    - Halfmove clock
    - Fullmove counter

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
        if fen_split[1] not in ('w', 'b'):
            raise ValueError("Black move")
        self.black_move = fen_split[1] == 'b'

        # Castling rights
        self.castling = 0
        castling = fen_split[2]
        if castling == '-':
            self.castling = 0
        else:
            for c in castling:
                self.castling |= CASTLE_MAP[c]  

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

        Detect the piece from given square.

        Includes sliders (rook, bishop, queen) and steppers (king without castling, knight)

        castling handled separately
        """
        
        piece = self.board[orig_sq]
        piece_type = get_type(piece)
        assert piece_type != EMPTY

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
        to_sqs = []

        direction = NN if get_color(piece) == WHITE else SS
        capture_dirs = (NE, NW) if get_color(piece) == WHITE else (SE, SW)
        home_row = 1 if get_color(piece) == WHITE else 6
       
        # try single step, including possible promotion
        step_sq = sq + direction
        # sq_valid test not needed because pawn can't be in rows 0 or 7
        if self.board[step_sq] == EMPTY:
            to_sqs.append(step_sq)


        # try double step if possible
        if sq_row(sq) == home_row:
            step2_sq = step_sq + direction
            # both squares in front must be empty
            if self.board[step_sq] == EMPTY and self.board[step2_sq] == EMPTY:
                to_sqs.append(step2_sq)

        # try capture (including en passant, based on position's target ep square)
        for dir in capture_dirs:
            capture_sq = sq + dir
            if sq_valid(capture_sq):
                capture_piece = self.board[capture_sq]
                if ((capture_piece != EMPTY and get_color(piece) != get_color(capture_piece)) or
                        capture_sq == self.ep_target):
                    to_sqs.append(capture_sq)

        # Generate moves, possibly with promotions
        for to_sq in to_sqs:
            if sq_row(to_sq) in (0, 7):
                for promo in (KNIGHT, BISHOP, ROOK, QUEEN):
                    yield Move(sq, to_sq, promotion=promo)
            else:
                yield Move(sq, to_sq)



    def is_attacked(self, sq, attacker_color):
        """Determine if square (possibly empty) is attacked by piece with given color"""
        
        for i in range(BOARD_SIZE):
            if not sq_valid(i): continue

            if get_color(self.board[i]) == attacker_color:
                attacks = self.generate_attacks(i)
                for move in attacks:
                    pass 

        return False
                

