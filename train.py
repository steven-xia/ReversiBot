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
import test

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
    pylab = None  # just to make my ide happy :P

sys.stdout.write(" Done\n")
sys.stdout.flush()

LOAD_INSTANCE = True
LOAD_FILE = "network1.pkl"
SAVE_FILE = "network2.pkl"
SECONDARY_SAVE_FILE = "network3.pkl"
DATA_FILE = "training_data.txt"

BATCH_SIZE = 100
ITERATIONS_PER_BATCH = 1
HIDDEN_LAYERS = (200, )

ALPHA = 0.0002
BETA = 0.95
DROPOUT_PERCENTAGE = 0.5
LAMBDA = 10 ** -9

VERBOSE_PER_EPOCH = 50
TEST_PER_EPOCH = 1
LOTS_GRAPH = True


def printf(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def convert_to_input(pieces):
    converted = []
    for row in pieces[:-1]:
        for piece in row:
            if piece == "X":
                converted += [1, 0]
            elif piece == "O":
                converted += [0, 1]
            else:
                converted += [0, 0]

    if pieces[-1] == "X":
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
        data = {}  # just to make my IDE happy :P
        exit(0)

    try:
        if GRAPH:
            pylab.xlabel("Iterations")
            pylab.ylabel("Accuracy (%)")
        positions = data.keys()
        GRAPH_FREQUENCY = len(data.keys()) / BATCH_SIZE + 1
        iteration = 0

        while True:
        
            spacer = "=" * 15
            print spacer + " EPOCH: {} ".format(round(float(brain.iteration) / (len(data) / BATCH_SIZE), 1) + 1) + spacer
        
            random.shuffle(positions)
            batches = [positions[n: n + BATCH_SIZE] for n in xrange(0, len(data), BATCH_SIZE)]
            error = 0
            
            for batch in batches:
                inputs = numpy.array(map(convert_to_input, batch), dtype=numpy.float32)
                outputs = numpy.array([[data[position]] for position in batch], dtype=numpy.float32)

                error += brain.train(inputs, outputs, iterations=ITERATIONS_PER_BATCH, alpha=ALPHA, beta=BETA,
                                     ladba=LAMBDA, dropout_percentage=DROPOUT_PERCENTAGE)
                iteration += ITERATIONS_PER_BATCH

                if iteration % (GRAPH_FREQUENCY / VERBOSE_PER_EPOCH) == 0:
                    current_error = error / ((iteration - 1) % GRAPH_FREQUENCY)
                    if LOTS_GRAPH:
                        pylab.scatter(brain.iteration, brain.error, c="b")
                        pylab.pause(10 ** -3)

                    deviation = 0
                    for weights in brain.weights_list:
                        deviation += numpy.std(weights)

                    print "Iteration: {} :: Accuracy: {}% :: Weights deviation: {}".format(
                        brain.iteration, round(brain.error, 2), round(deviation, 4))

                # if iteration % (GRAPH_FREQUENCY / TEST_PER_EPOCH) == 0:
                #     printf("Testing network... ")
                #     test_accuracy = test.test(brain)
                #     printf("Done\n")
                #     if LOTS_GRAPH:
                #         pylab.scatter(brain.iteration, test_accuracy, c="r")
                #         pylab.pause(10 ** -3)

                #     print "Iteration: {} :: Test Accuracy: {}%".format(
                #         brain.iteration, round(test_accuracy, 2))

                if iteration % GRAPH_FREQUENCY == 0 and GRAPH:
                    pylab.scatter(brain.iteration, brain.error, c="b")
                    pylab.pause(10 ** -3)

                if brain.iteration % 100000 == 0:
                    printf("Saving network as secondary... ")
                    f = open(SECONDARY_SAVE_FILE, "w")
                    cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
                    f.close()
                    printf("Done\n")

            print "Iteration: {}  -> ".format(brain.iteration),
            printf("Saving network... ")
            f = open(SAVE_FILE, "w")
            cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
            f.close()
            printf("Done\n")

    except KeyboardInterrupt:
        brain.iteration = int(round(brain.iteration / 100.0)) * 100

        f = open(SAVE_FILE, "w")
        cPickle.dump(brain, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

    pylab.show()
    print
