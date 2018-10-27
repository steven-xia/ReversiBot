"""
File: collect_data.py

Description: Run this to collect training data with the 'Edax' engine.

NOTE ON COPYRIGHT: I DO NO OWN THE 'EDAX' ENGINE AND ALL RIGHTS STAY WITH THE
CREATOR OF THE ENGINE.

NOTE: It has a stupid error thingy (It doesn't crash though). :P

"""

import math
import sys

import numpy
import random

import datafile_manager
import edax_wrapper
import reversi

DATA_FILE = "training_data.txt"
TEST_FILE = "testing_data.txt"

DEPTH = 16

# Uncomment to collect test data (currently not used).
# DATA_FILE, TEST_FILE = TEST_FILE, DATA_FILE


CONVERSION_CHART = {
    "X": 0,
    "O": 1,
    "-": 2
}

CONVERSION_CHART2 = {
    0: "X",
    1: "O",
    2: "-"
}


def rotate(pieces):
    converted = [[]] * 8
    for row in xrange(8):
        converted[row] = [int(CONVERSION_CHART[piece])
                          for piece in str(pieces[row * 8: row * 8 + 8])]
    converted = numpy.rot90(numpy.array(converted))
    converted = "".join(CONVERSION_CHART2[piece]
                        for row in converted for piece in row)
    return converted + pieces[-1]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


if __name__ == "__main__":
    try:
        sys.stdout.write("Loading data file... ")
        sys.stdout.flush()
        data = datafile_manager.load_data(DATA_FILE)
        sys.stdout.write("Done\n")
    except IOError:
        sys.stdout.write("data file not found, starting with empty dataset.\n")
        data = {}
    sys.stdout.flush()

    try:
        sys.stdout.write("Loading test file... ")
        sys.stdout.flush()
        test = datafile_manager.load_data(TEST_FILE)
        sys.stdout.write("Done\n")
    except IOError:
        sys.stdout.write("test file not found, starting with empty dataset.\n")
        test = {}
    sys.stdout.flush()

    try:
        while True:
            # sys.stdout.write("Initializing board... ")
            b = reversi.Board()
            # sys.stdout.write("Done\n")

            while not b.is_over() and len(b.available_positions) > 8:
                # sys.stdout.write("Choosing random move... ")
                random_move = random.choice(b.legal_moves_notation)
                b.move(random_move)
                # sys.stdout.write("Move: {}\n".format(random_move))

                position = b.get_pieces()
                sys.stdout.write("New position: {}\n".format(position))

                sys.stdout.write("Evaluating position... ")
                score = edax_wrapper.get_evaluation(position, depth=DEPTH)
                sys.stdout.write("Score: {}, ".format(score))
                score = sigmoid(score)
                sys.stdout.write("Percentage: {}\n".format(score))

                if type(score) != float:
                    sys.stdout.write("\nWARNING: That stupid error occured again... restarting Edax... ")
                    edax_wrapper.terminate()
                    edax_wrapper._initialize()
                    sys.stdout.write("Done.\n")
                    continue

                augmented_positions = [position]
                for _ in xrange(3):
                    position = rotate(position)
                    augmented_positions.append(position)

                for position in augmented_positions:
                    if position not in data.keys() + test.keys():
                        sys.stdout.write("Adding position: {}\n".format(position))
                        data[position] = score

                        if len(data) % 1000 == 0:
                            sys.stdout.write("{} entries, saving data... ".format(
                                len(data)
                            ))

                            datafile_manager.save_data(data, DATA_FILE)
                            sys.stdout.write("Done\n")

                    else:
                        sys.stdout.write("Position already saved, continuing.\n")

            sys.stdout.write("Resetting board... ")
            edax_wrapper.new_position()
            sys.stdout.write("Done\n")

    except KeyboardInterrupt:
        sys.stdout.write("\nKeyboardInterrupt: saving data... ")
        sys.stdout.flush()
        datafile_manager.save_data(data, DATA_FILE)
        sys.stdout.write("Done\n")
        sys.stdout.flush()

        sys.stdout.write("New dataset size: {}\n".format(len(data)))

    except Exception as error:
        sys.stdout.write("WARNING: UNEXPECTED ERROR: {}\n".format(error))

        sys.stdout.write("Saving data... ")
        sys.stdout.flush()
        datafile_manager.save_data(data, DATA_FILE)
        sys.stdout.write("Done\n")
        sys.stdout.flush()

        sys.stdout.write("New dataset size: {}\n".format(len(data)))

    finally:
        edax_wrapper.terminate()
