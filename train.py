#! /usr/bin/python

"""
file: train.py  -- version 0.2.1

Description: Simple training algorithm using the 'neural_network.py' module.
"""


import sys

sys.stdout.write("Importing modules.")
sys.stdout.flush()
import datafile_manager
import neural_network

sys.stdout.write(".")
sys.stdout.flush()

import cPickle
import numpy
import random

sys.stdout.write(".")
sys.stdout.flush()

import pylab

sys.stdout.write(" Done\n")
sys.stdout.flush()

LOAD_INSTANCE = True
LOAD_FILE = "network1.pkl"
SAVE_FILE = "network2.pkl"
SECONDARY_SAVE_FILE = "network3.pkl"
DATA_FILE = "training_data.txt"

BATCH_SIZE = 10
ITERATIONS_PER_BATCH = 1
HIDDEN_LAYERS = (100, )

GRAPH_FREQUENCY = 4000

ALPHA = 0.01
DROPOUT_PERCENTAGE = 0.2


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
    if LOAD_INSTANCE:
        f = open(LOAD_FILE, "r")
        brain = cPickle.load(f)
        f.close()
    else:
        brain = neural_network.NeuralNetwork(input_layer_size=129,
                                             hidden_layer_sizes=HIDDEN_LAYERS,
                                             output_layer_size=1)

    try:
        sys.stdout.write("Loading data file... ")
        sys.stdout.flush()
        data = datafile_manager.load_data(DATA_FILE)
        sys.stdout.write("Done\n")
        sys.stdout.flush()
    except IOError:
        print "Data file not found, quitting... "
        exit(0)

    try:
        positions = data.keys()
        while True:
            random.shuffle(positions)
            batches = [positions[n: n + BATCH_SIZE] for n in xrange(0, len(data), BATCH_SIZE)]
            for batch in batches:
                # sys.stdout.write("Determining new batch inputs and outputs... ")
                inputs = numpy.array(map(convert_to_input, batch), dtype=numpy.float128)
                outputs = numpy.array([[data[position]] for position in batch], dtype=numpy.float128)
                # sys.stdout.write("Done\n")

                if "error" in globals():
                    error += brain.train(inputs, outputs, iterations=ITERATIONS_PER_BATCH, alpha=ALPHA,
                                         dropout_percentage=0.2,
                                         verbose=100)
                else:
                    brain.train(inputs, outputs, iterations=ITERATIONS_PER_BATCH, alpha=ALPHA,
                                dropout_percentage=DROPOUT_PERCENTAGE,
                                verbose=100)

                if brain.iterations % GRAPH_FREQUENCY == 0:
                    if "error" in globals():
                        pylab.scatter(brain.iterations, ITERATIONS_PER_BATCH * error / GRAPH_FREQUENCY, c="b")
                        pylab.pause(10 ** -3)
                    error = 0

                if brain.iterations % 10000 == 0:
                    sys.stdout.write("Saving network... ")
                    f = open(SAVE_FILE, "w")
                    cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
                    f.close()
                    sys.stdout.write("Done\n")

                if brain.iterations % 100000 == 0:
                    sys.stdout.write("Saving network as secondary... ")
                    f = open(SECONDARY_SAVE_FILE, "w")
                    cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
                    f.close()
                    sys.stdout.write("Done\n")

    except KeyboardInterrupt:
        brain.iterations = int(round(brain.iterations / 100.0)) * 100

        f = open(SAVE_FILE, "w")
        cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

    pylab.show()
    print
