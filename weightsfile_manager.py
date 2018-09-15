"""
File: weightsfile_manager.py  -- version 0.1

Description: Helper module for interaction with the weights file.

NOTE: This is currently not actually used because the current storage
implementation is using cPickle (it's just easier that way :).
"""

import numpy


def save_weights(weight_sets, filename):
    save_string = ""
    for weight_set in weight_sets:
        for weights in weight_set:
            save_string += " ".join(list(map(str, weights))) + "\n"
        save_string += "-\n"

    save_file = open(filename, "w")
    save_file.write(save_string)
    save_file.close()


def load_weights(filename):
    load_file = open(filename, "r")
    data = load_file.read()
    load_file.close()

    weight_sets = data.split("-\n")[:-1]
    weight_sets = [weights.split("\n")[:-1] for weights in weight_sets]
    for weight_set in weight_sets:
        for weights_index in xrange(len(weight_set)):
            weight_set[weights_index] = map(float, weight_set[weights_index].split())
    weight_sets = [numpy.array(weights) for weights in weight_sets]

    return weight_sets


if __name__ == "__main__":
    pass
