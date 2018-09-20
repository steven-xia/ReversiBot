"""
File: collect_data.py  -- version 0.1.1

Description: Run this to collect training data with the 'Edax' engine.

NOTE ON COPYRIGHT: I DO NO OWN THE 'EDAX' ENGINE AND ALL RIGHTS STAY WITH THE
CREATOR OF THE ENGINE.

NOTE: It has a stupid error thingy (It doesn't crash though). :P
"""

import datafile_manager
import edax_wrapper
import reversi

import random
import sys
import math

DATA_FILE = "training_data.txt"


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
        while True:
            # sys.stdout.write("Initializing board... ")
            b = reversi.Board()
            # sys.stdout.write("Done\n")

            while not b.is_over():
                # sys.stdout.write("Choosing random move... ")
                random_move = random.choice(b.legal_moves_notation)
                b.move(random_move)
                # sys.stdout.write("Move: {}\n".format(random_move))

                position = b.get_pieces()
                sys.stdout.write("New position: {}\n".format(position))

                if position not in data.keys():
                    sys.stdout.write("Position not in dataset, evaluating position... ")
                    score = edax_wrapper.get_evaluation(position)
                    if type(score) != float:
                        sys.stdout.write("\nWARNING: That stupid error occured again... restarting Edax... ")
                        edax_wrapper.terminate()
                        edax_wrapper._initialize()
                        sys.stdout.write("Done.\n")
                        continue

                    sys.stdout.write("Score: {}, ".format(score))
                    score = sigmoid(score)
                    sys.stdout.write("Percentage: {}\n".format(score))

                    data[position] = score

                    if len(data) % 10000 == 0:
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
        print "WARNING: UNEXPECTED ERROR:", error

        sys.stdout.write("Saving data... ")
        sys.stdout.flush()
        datafile_manager.save_data(data, DATA_FILE)
        sys.stdout.write("Done\n")
        sys.stdout.flush()

        sys.stdout.write("New dataset size: {}\n".format(len(data)))

    finally:
        edax_wrapper.terminate()
