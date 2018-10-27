"""
File: evaluator_ab.py -- version 0.2.1

Description: Evaluation module for evaluating a reversi board state... This was
copied from an older program.
"""

EMPTY = 2

MOBILITY_FACTOR = 10
FRONTIER_FACTOR = 2
LESS_PIECE_FACTOR = 0.01

piece_scores = [
    [199, -8, 8, 6, 6, 8, -8, 199],
    [-8, -24, -4, -3, -3, -4, -24, -8],
    [8, -4, 7, 4, 4, 7, -4, 8],
    [6, -3, 4, 0, 0, 4, -3, 6],
    [6, -3, 4, 0, 0, 4, -3, 6],
    [8, -4, 7, 4, 4, 7, -4, 8],
    [-8, -24, -4, -3, -3, -4, -24, -8],
    [199, -8, 8, 6, 6, 8, -8, 199],
]

NOT_ALLOWED = frozenset([(x, y) for x in [-1, 8] for y in xrange(-1, 9)] +
                        [(x, y) for x in xrange(8) for y in [-1, 8]])
NOT_ALLOWED = {x: True for x in NOT_ALLOWED}

SIDE_FACTORS = {0: 1, 1: -1, 2: 0}


def evaluate(board):
    pieces = board.pieces

    if board.is_over():
        score = board.score()
        return 100 * (score[0] - score[1])

    score = 0

    # Pieces and values...
    empty_places = 0
    colors = 0
    positions = 0

    for row_index in xrange(len(pieces)):
        for column_index in xrange(len(pieces[row_index])):
            if pieces[row_index][column_index] == 0:
                colors += 1
                positions += piece_scores[row_index][column_index]
            elif pieces[row_index][column_index] == 1:
                colors -= 1
                positions -= piece_scores[row_index][column_index]
            else:
                empty_places += 1

    position_value = min(1, 0.1 * empty_places)
    piece_value = 100 - 10 * empty_places
    piece_value = max(LESS_PIECE_FACTOR * piece_value, piece_value)
    score += colors * piece_value

    # Mobility...
    temporary_score = 0
    for _ in xrange(2):
        board.move(None)
        factor = SIDE_FACTORS[board.side]
        if board.legal_moves == [None]:
            temporary_score -= factor * 5 * MOBILITY_FACTOR
        elif len(board.legal_moves) == 1:
            temporary_score -= factor * MOBILITY_FACTOR
        else:
            temporary_score += factor * MOBILITY_FACTOR * \
                               len(board.legal_moves)

    temporary_score *= SIDE_FACTORS[board.side]
    positions += temporary_score

    # Frontier minimization...
    for rindex, row in enumerate(board.pieces):
        for cindex, piece in enumerate(row):
            if board.pieces[rindex][cindex] == EMPTY:
                continue

            side_factor = SIDE_FACTORS[board.pieces[rindex][cindex]]

            around = (
                (rindex - 1, cindex - 1),
                (rindex - 1, cindex),
                (rindex - 1, cindex + 1),
                (rindex, cindex - 1),
                (rindex, cindex + 1),
                (rindex + 1, cindex - 1),
                (rindex + 1, cindex),
                (rindex + 1, cindex + 1)
            )

            for coordinate in around:
                if coordinate in NOT_ALLOWED:
                    continue
                if board.pieces[coordinate[0]][coordinate[1]] == EMPTY:
                    positions -= side_factor * FRONTIER_FACTOR
                    break

    score += positions * position_value

    return score
