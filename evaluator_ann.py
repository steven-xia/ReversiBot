"""
File: evaluator_nn.py

Description: This evaluation module uses a pre-trained neural network.
"""

import cPickle

import numpy
import random

INSTANCE_FILE = "network.pkl"
LOOK_NICE = False

f = open(INSTANCE_FILE, "rb")
brain = cPickle.load(f)
f.close()

NOISE_FACTOR = 0.00


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

    if board.side == 0:
        converted += [1, 0]
    else:
        converted += [0, 1]

    return converted


def evaluate(board):
    if board.is_over():
        score = board.score()
        return 100 * (score[0] - score[1])

    pieces = board.pieces
    empty_places = 0
    ascore = 0
    for row_index in xrange(len(pieces)):
        for column_index in xrange(len(pieces[row_index])):
            if pieces[row_index][column_index] == 2:
                empty_places += 1
            elif pieces[row_index][column_index] == 0:
                ascore += 1
            else:
                ascore -= 1
    count_pieces = 8.0
    if empty_places > count_pieces:
        ascore *= (empty_places - count_pieces) / count_pieces
    else:
        ascore = 0

    inputs = numpy.array([convert_to_input(board)])
    output = brain.think(inputs)[0][0]
    output = -100 * numpy.log(1 / output - 1 + 10 ** -8)  # Convert to pieces.
    noise = 1 + (NOISE_FACTOR) * (2 * random.random() - 1)
    return noise * output + ascore
