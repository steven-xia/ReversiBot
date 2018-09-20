#! /usr/bin/python

"""
file: train.py  -- version 0.2.2

Description: Simple training 'algorithm' using the 'neural_network.py' module.
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

try:
    GRAPH = True
    import pylab
except ImportError:
    GRAPH = False

sys.stdout.write(" Done\n")
sys.stdout.flush()

LOAD_INSTANCE = True
LOAD_FILE = "network1.pkl"
SAVE_FILE = "network2.pkl"
SECONDARY_SAVE_FILE = "network3.pkl"
DATA_FILE = "training_data.txt"

BATCH_SIZE = 100
ITERATIONS_PER_BATCH = 1
HIDDEN_LAYERS = (144, 89)

ALPHA = 0.00005
BETA = 0.99
DROPOUT_PERCENTAGE = 0.5
LAMBDA = 10 ** -6

VERBOSE_PER_EPOCH = 100


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
        error = 0

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
        if GRAPH:
            pylab.xlabel("Iterations")
            pylab.ylabel("Accuracy (%)")
        positions = data.keys()
        GRAPH_FREQUENCY = len(data.keys()) / BATCH_SIZE + 1
        iteration = 0

        while True:
            random.shuffle(positions)
            batches = [positions[n: n + BATCH_SIZE] for n in xrange(0, len(data), BATCH_SIZE)]
            error = 0
            
            for batch in batches:
                inputs = numpy.array(map(convert_to_input, batch), dtype=numpy.float64)
                outputs = numpy.array([[data[position]] for position in batch], dtype=numpy.float64)

                error += brain.train(inputs, outputs, iterations=ITERATIONS_PER_BATCH, alpha=ALPHA, beta=BETA, ladba=LAMBDA,
                                     dropout_percentage=0.2)
                iteration += ITERATIONS_PER_BATCH

                if iteration % (GRAPH_FREQUENCY / VERBOSE_PER_EPOCH) == 0:
                    current_error = error / ((iteration - 1) % GRAPH_FREQUENCY)
                    print "Iteration: {} :: Accuracy {}%".format(brain.iteration, round(current_error, 2))

                if iteration % GRAPH_FREQUENCY == 0 and GRAPH:
                    pylab.scatter(brain.iteration, error / GRAPH_FREQUENCY, c="b")
                    pylab.pause(10 ** -3)

                if brain.iteration % 100000 == 0:
                    sys.stdout.write("Saving network as secondary... ")
                    f = open(SECONDARY_SAVE_FILE, "w")
                    cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
                    f.close()
                    sys.stdout.write("Done\n")

            print "Iteration: {}  -> ".format(brain.iteration),
            sys.stdout.write("Saving network... ")
            f = open(SAVE_FILE, "w")
            cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
            f.close()
            sys.stdout.write("Done\n")
            
            print "=" * 40

    except KeyboardInterrupt:
        brain.iteration = int(round(brain.iteration / 100.0)) * 100

        f = open(SAVE_FILE, "w")
        cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

    pylab.show()
    print
