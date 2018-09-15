#! /usr/bin/python

"""
file: find_alpha.py  -- version 0.2.2

Description: Adaptation of 'play.py' to find the optimal alpha for a certain
network size/architecture. Sometimes doesn't work?

Dependencies:
  - pylab (matplotlib)
  - numpy
"""

import sys

sys.stdout.write("Importing modules.")
sys.stdout.flush()
import datafile_manager
import neural_network
import copy

sys.stdout.write(".")
sys.stdout.flush()

import numpy
import random

sys.stdout.write(".")
sys.stdout.flush()

try:
    PYLAB = True
    import pylab
except ImportError:
    PYLAB = False
    pylab = []

sys.stdout.write(" Done\n")
sys.stdout.flush()

DATA_FILE = "training_data.txt"

HIDDEN_LAYERS = ()

BATCH_SIZE = 100
ITERATIONS_PER_BATCH = 1

GRAPH_FREQUENCY = 9999
ALPHA = 0.0001
DROPOUT_PERCENTAGE = 0.0


def convert_to_input(pieces):
    converted = []
    for piece in pieces[:-1]:
        if piece == "X":
            converted += [1, 0]
        elif piece == "O":
            converted += [0, 1]
        else:
            converted += [0, 0]

    if pieces[:-1] == "X":
        converted.append(0)
    else:
        converted.append(1)

    return converted


if __name__ == "__main__":
    brain = neural_network.NeuralNetwork(input_layer_size=129,
                                         hidden_layer_sizes=HIDDEN_LAYERS,
                                         output_layer_size=1)
    weights = copy.deepcopy(brain.weights_list)

    try:
        sys.stdout.write("Loading data file... ")
        sys.stdout.flush()
        data = datafile_manager.load_data(DATA_FILE)
        sys.stdout.write("Done\n")
        sys.stdout.flush()
    except IOError:
        print "Data file not found, quitting... "
        exit(0)

    positions = data.keys()
    random.shuffle(positions)
    batches = [positions[n: n + BATCH_SIZE] for n in xrange(0, len(data), BATCH_SIZE)]

    thingy = 0
    while True:
        error = 0
        print "ALPHA:", ALPHA
        random.seed(0)
        for batch in batches:
            inputs = numpy.array(map(convert_to_input, batch), dtype=numpy.float128)
            outputs = numpy.array([[data[position]] for position in batch], dtype=numpy.float128)

            error += brain.train(inputs, outputs, iterations=ITERATIONS_PER_BATCH, alpha=ALPHA,
                                 dropout_percentage=DROPOUT_PERCENTAGE,
                                 verbose=100)

        thingy += 1
        brain = neural_network.NeuralNetwork(input_layer_size=129,
                                             hidden_layer_sizes=HIDDEN_LAYERS,
                                             output_layer_size=1)

        if PYLAB:
            pylab.scatter(thingy, error)
            pylab.pause(10 ** -3)
        else:
            pylab.append((ALPHA, error))

        ALPHA *= 2
        if ALPHA > 10:
            break

    if PYLAB:
        pylab.show()
    else:
        print
        print "Results: "
        for alpha, error in pylab:
            print "Alpha: {} :: Error: {}".format(alpha, error)
