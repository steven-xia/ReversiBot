"""
File: play.py

Description: Run to play the computer. Edit the CONSTANTS to change how the
computer player plays. This is the original play file; it is now ported to
"gui.py". Although a little out-dated, this should still be more functional
"gui.py".

Dependencies:
  - pylab (matplotlib)

TODO: Really clean up the code.
"""

print
import sys

sys.stdout.write("Importing modules.")
sys.stdout.flush()
import time
# import math

import searcher
import evaluator_ab
import evaluator_nn
import evaluator_test

import searcher_test as searcher

sys.stdout.write(".")
sys.stdout.flush()

STATS = False

try:
    GRAPH = True
    import pylab
except ImportError:
    GRAPH = False

sys.stdout.write(". Done\n")
sys.stdout.flush()
print

FIRST_EVALUATOR = evaluator_test.evaluate
SECOND_EVALUATOR = evaluator_nn.evaluate

LEVEL = 0
SPEED_FACTOR = 9 - LEVEL
MINIMUM_DEPTH = 2
time_func = lambda t: ((t - 13)/10.5)**3 - ((t - 20)/3.5)**2 + 60
TIME = map(time_func, range(100))
TIME = map(lambda n: n / 6, TIME)

MINIMUM = -1
MAXIMUM = 1

SMOOTH_FACTOR = 0.0
ONE_AVERAGE = 0
TWO_AVERAGE = 0

if GRAPH:
    pylab.axhline(linewidth=0.1, color="k")
    # pylab.yscale("symlog")


def computer_move_timed(engine):
    global turn
    turn += 1

    # if engine.board.side == 0:
    #     engine.timed_expand(TIME[turn])
    # else:
    #     engine.timed_expand(TIME2[turn])

    total_start_time = time.time()
    total_start_nodes = engine.number_nodes()

    engine.timed_expand(TIME[turn])

    while engine.fully_expanded - int(not engine.caught_up) < MINIMUM_DEPTH:
        # if engine.board.side == 0 and \
        #         not engine.fully_expanded - int(not engine.caught_up) < MINIMUM_DEPTH:
        #     break
        # if engine.board.side == 1 and \
        #         not engine.fully_expanded - int(not engine.caught_up) < MINIMUM_DEPTH2:
        #     break

        starting_nodes = engine.number_nodes()
        start_time = time.time()
        engine.expand()
        end_time = time.time()
        ending_nodes = engine.number_nodes()

        expanded_nodes = ending_nodes - starting_nodes
        nodes_per_second = int(float(expanded_nodes) /
                               (end_time - start_time))

        print "{} ply :: expanded {} nodes @ {} nodes/sec".format(
            engine.fully_expanded,
            expanded_nodes,
            nodes_per_second
        )

    print "{} ply :: {} nodes".format(engine.fully_expanded,
                                      engine.number_nodes())

    print "Evaluating nodes...",
    sys.stdout.flush()
    engine.update_scores()

    total_nodes = engine.number_nodes() - total_start_nodes
    total_efficiency = int(total_nodes / (time.time() - total_start_time))
    print "Done"

    print "Average speed {} nodes @ {} nodes/sec".format(
        total_nodes,
        total_efficiency
    )

    print
    print "Bot legal moves:", engine.board.legal_moves_notation
    print "Bot move:", engine.best_move()
    print "Bot evaluation:", round(float(engine.game_tree.score) / 100, 2)
    print

    if GRAPH:
        global MAXIMUM, MINIMUM
        global ONE_AVERAGE, TWO_AVERAGE

        score = round(float(engine.game_tree.score) / 100, 2)

        if turn % 2 == 0:
            TWO_AVERAGE = SMOOTH_FACTOR * TWO_AVERAGE + (1 - SMOOTH_FACTOR) * score
            TWO_AVERAGE = min(max(TWO_AVERAGE, -4.0), 4.0)
            pylab.scatter(turn, TWO_AVERAGE, c="r")
            score = TWO_AVERAGE
        else:
            ONE_AVERAGE = SMOOTH_FACTOR * ONE_AVERAGE + (1 - SMOOTH_FACTOR) * score
            ONE_AVERAGE = min(max(ONE_AVERAGE, -4.0), 4.0)
            pylab.scatter(turn, round(ONE_AVERAGE, 1), c="b")
            score = ONE_AVERAGE

        MINIMUM = min(score - 0.5, MINIMUM)
        MAXIMUM = max(score + 0.5, MAXIMUM)

        MINIMUM = min(-MAXIMUM, MINIMUM)
        MAXIMUM = max(-MINIMUM, MAXIMUM)

        pylab.axis((0, turn + 1, MINIMUM, MAXIMUM))
        pylab.pause(0.01)

    engine.move(engine.best_move())
    engine.board.display()


def human_move(engine):
    global turn
    turn += 1

    print "Legal moves:", engine.board.legal_moves_notation

    while True:

        move = raw_input("Your move: ")

        if move in engine.board.legal_moves_notation:
            break

        if move.lower() in ("none", "") and \
                engine.board.legal_moves_notation == [None]:
            move = None
            break

    print
    engine.move(move)
    engine.board.display()


def main():
    bot = searcher.Searcher((FIRST_EVALUATOR, SECOND_EVALUATOR))
    bot.board.display()
    bot.expand()

    if len(sys.argv) == 1:
        sys.argv.append("black")

    if sys.argv[1] == "white":
        computer_move_timed(bot)

    while not bot.board.is_over():

        if sys.argv[1] != "bot":
            if bot.board.is_over():
                break
            human_move(bot)

        if bot.board.is_over():
            break
        computer_move_timed(bot)

    print "Final score:", " - ".join(map(str, bot.board.score()))


if __name__ == "__main__":
    turn = 0

    if STATS:
        import cProfile
        import pstats

        bot = searcher.Searcher(evaluator_ab.evaluate)
        cProfile.run('main()', 'main.profile')
        stats = pstats.Stats('main.profile')
        stats.strip_dirs().sort_stats('time').print_stats()
    else:
        main()

    if GRAPH:
        pylab.show()
