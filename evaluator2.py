"""
File: evaluator2.py -- version 0.1.1

Description: This evaluation module uses a pre-trained neural network.
"""


import cPickle
import numpy

INSTANCE_FILE = "network.pkl"

f = open(INSTANCE_FILE, "r")
brain = cPickle.load(f)
f.close()


def convert_to_input(board):
    pieces = board.pieces
    converted = []
    for row in pieces:
        for piece in row:
            if piece == 0:
                converted += [1, 0]
            elif piece == 1:
                converted += [0, 1]
            else:
                converted += [0, 0]
    converted.append(board.side)
    return converted


def evaluate(board):
    if board.is_over():
        score = board.score()
        return 100 * (score[0] - score[1])

    inputs = numpy.array([convert_to_input(board)])
    output = brain.think(inputs)
    output = -100 * numpy.log(1 / output - 1)  # Convert to pieces.
    return output
