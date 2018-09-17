#! /usr/bin/python

"""
file: gui.py  -- version 0.1.1

Description: Main part of program, using Tkinter windows for pretty display,
otherwise, 'play.py' has more functionality.

Dependencies:
  - Tkinter
"""

import sys

import Tkinter
import tkMessageBox

import searcher
import evaluator
import evaluator2

try:
    root = Tkinter.Tk()
    root.title("Reversi")

    LEVEL = 1
    PLAYER = "black"
    for argument in sys.argv[1:]:
        attribute, value = map(lambda x: x.lower(), argument.split("="))
        if attribute == "player":
            if value in ("black", "white"):
                PLAYER = value
            else:
                message = "'{}' not a valid argument for 'player'; using " \
                          "default: black".format(value)
                tkMessageBox.showwarning(title="Warning", message=message)
        elif attribute == "level":
            value = int(value)
            if value in range(11):
                LEVEL = value
            else:
                message = "'{}' not a valid argument for 'level'; using " \
                          "default: 1".format(value)
                tkMessageBox.showwarning(title="Warning", message=message)
except:
    PLAYER = "black"
    LEVEL = 1
    message = "There's something wrong with your command; continuing with " \
              "default values."
    tkMessageBox.showerror(title="Error", message=message)

EVALUATOR = evaluator2.evaluate
SPEED_FACTOR = 9 - LEVEL
MINIMUM_DEPTH = int(2 + LEVEL / 4)

if EVALUATOR == evaluator.evaluate:
    TIME = [0.5] * 52 + [9999] * 20
elif EVALUATOR == evaluator2.evaluate:
    TIME = [0.2] * 52 + [9999] * 20
else:
    raise Exception("NANI???")
TIME = map(lambda x: LEVEL * x, TIME)

turn = 0

COLORS = ("black", "white", "green4", "chartreuse3")
HIGHLIGHT_COLORS = ("gray8", "gray96", "green4", "chartreuse2")
COMPUTER_MOVING = False


def callback(coordinate):
    global COMPUTER_MOVING, root, bot, turn

    if COMPUTER_MOVING:
        return

    if coordinate in bot.board.legal_moves:
        move = bot.board.convert_to_notation(coordinate)

        turn += 1
        COMPUTER_MOVING = True

        bot.move(move)
        update(bot.board.pieces)

        status_label.config(text="Thinking...")
        root.after(10, computer_move)
    elif bot.board.legal_moves == [None]:
        move = None

        turn += 1
        COMPUTER_MOVING = True

        bot.move(move)
        update(bot.board.pieces)

        status_label.config(text="Thinking...")
        root.after(10, computer_move)


def computer_move():
    global COMPUTER_MOVING, status_label, root, bot, turn
    turn += 1

    bot.timed_expand(TIME[turn])
    # while bot.fully_expanded - int(not bot.caught_up) < MINIMUM_DEPTH:
    #     bot.expand()

    bot.update_scores()
    bot.move(bot.best_move())

    update(bot.board.pieces)

    if bot.board.is_over():
        score = bot.board.score()
        if (score[0] - score[1] > 0 and PLAYER == "black") or \
                (score[0] - score[1] < 0 and PLAYER == "white"):
            message = "Hey... you won...\nScore: {}".format(score)
            tkMessageBox.showinfo(title="You Win!", message=message)
        else:
            message = "Guess what? You suck!\nScore: {}".format(score)
            tkMessageBox.showinfo(title="You Lost!", message=message)
        status_label.config(text="Score: {}".format(bot.board.score()))
    elif bot.board.legal_moves == [None]:
        tkMessageBox.showinfo(title="Get rekt!", message="You have no moves... ")
        bot.move(None)
        root.after(10, computer_move)
    else:
        status_label.config(text="Your turn.")
        COMPUTER_MOVING = False


def update(pieces):
    global function_list, bot

    for row_index, row in enumerate(pieces):
        for column_index, piece in enumerate(row):
            if (row_index, column_index) in bot.board.legal_moves:
                function_list[row_index * 8 + column_index](3)
            else:
                function_list[row_index * 8 + column_index](piece)

    global information_label, evaluation_label
    information = "{} :: {} nodes".format(bot.fully_expanded,
                                          bot.number_nodes())
    information_label.config(text=information)
    evaluation = "Evaluation: {}".format(round(bot.game_tree.score / 100, 2))
    evaluation_label.config(text=evaluation)


if __name__ == "__main__":

    # Suppress the useless output... :D
    import os
    import sys

    sys.stdout = open(os.devnull, "w")

    bot = searcher.Searcher((EVALUATOR, EVALUATOR))
    bot.update_scores()

    button = Tkinter.Button(root, font=("Comic Sans MS", 10, "bold"),
                            foreground="red", width=7,
                            text="QUIT", command=quit)
    button.grid(row=0, column=7)

    function_list = []
    for row in xrange(8):
        for column in xrange(8):
            foo = lambda row=row, column=column: callback((row, column))
            button = Tkinter.Button(root, height=4, width=8,
                                    relief=Tkinter.FLAT, command=foo)
            button.grid(row=row + 1, column=column)

            foo = lambda side, button=button: \
                button.config(background=COLORS[side],
                              activebackground=HIGHLIGHT_COLORS[side])
            function_list.append(foo)

            root.update()
    for row_index, row in enumerate(bot.board.pieces):
        for column_index, piece in enumerate(row):
            if (row_index, column_index) in bot.board.legal_moves:
                function_list[row_index * 8 + column_index](3)
            else:
                function_list[row_index * 8 + column_index](piece)
            root.update()

    root.update()

    status_label = Tkinter.Label(master=root,
                                 font=("Comic Sans MS", 10, "bold italic"),
                                 text="Your turn.")
    status_label.grid(row=0, column=0, columnspan=2)

    information_label = Tkinter.Label(master=root,
                                      font=("Comic Sans MS", 10, "bold"))
    information_label.grid(row=0, column=2, columnspan=2)

    evaluation_label = Tkinter.Label(master=root,
                                     font=("Comic Sans MS", 10, "bold"))
    evaluation_label.grid(row=0, column=4, columnspan=2)

    level_label = Tkinter.Label(master=root,
                                font=("Comic Sans MS", 10, "bold"),
                                text="Level: {}".format(LEVEL))
    level_label.grid(row=0, column=6)

    update(bot.board.pieces)

    root.update()
    root.resizable(width=False, height=False)

    if PLAYER == "white":
        turn += 1
        COMPUTER_MOVING = True

        status_label.config(text="Thinking...")
        root.after(10, computer_move)

    root.mainloop()
