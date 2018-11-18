"""
File: edax_wrapper.py

Description: Wrapper module for interaction with the Edax engine.
"""

import time

import subprocess

THREADS = 2
EDAX_LOCATION = "./Edax/edax-4.4"
EDAX_COMMAND = "{} -cassio -n-tasks {}".format(
    EDAX_LOCATION,
    THREADS
)


def _initialize():
    global process

    process = subprocess.Popen(EDAX_COMMAND, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write("ENGINE-PROTOCOL init\n")
    process.stdin.flush()
    process.stdout.readline()


def terminate():
    global process

    try:
        process.stdin.write("ENGINE-PROTOCOL quit\n")
        process.stdin.flush()

        process.stdin.close()
        process.terminate()
        process.wait()
    except IOError:
        pass


def get_evaluation(position, search_time=60, depth=16, probcut_precision=100):
    global process, last_position
    last_position = position

    end_time = time.time() + search_time
    evaluation = 0

    for current_depth in xrange(2, depth + 1, 2):
        search_string = "ENGINE-PROTOCOL midgame-search {} -64 64 {} {}\n".format(
            position, current_depth, probcut_precision
        )

        process.stdin.write(search_string)
        process.stdin.flush()
        output = process.stdout.readline()[:-1].split()
        if len(output) < 16:
            return "STUPID ERROR!"
        process.stdout.readline()

        if position[-1] == "X":
            minimum = float(output[6][1:])
            maximum = float(output[10][1:-1])
        else:
            minimum = -float(output[6][1:])
            maximum = -float(output[10][1:-1])
        evaluation = (minimum + maximum) / 2

        if end_time - time.time() < 0:
            break

        time.sleep(0.01)  # Make sure the the inputs don't get messed up... :P

    return evaluation


def best_move():
    global process, last_position

    search_string = "ENGINE-PROTOCOL midgame-search {} -64 64 {} {}\n".format(
        last_position, 0, 100
    )

    process.stdin.write(search_string)
    process.stdin.flush()
    output = process.stdout.readline()[:-1].split()
    process.stdout.readline()

    move = output[2]
    move = move[0].lower() + move[1]

    return move


def new_position():
    global process

    process.stdin.write("ENGINE-PROTOCOL new-position\n")
    process.stdin.flush()
    process.stdout.readline()


_initialize()

if __name__ == "__main__":
    terminate()
