"""
File: searcher.py  -- version 0.1.1

Description: Searcher module with simple lookahead logic...

Dependencies:
  - anytree

TODO: Find the time to rewrite with speed optimizations in mind.
"""

import anytree
import reversi

import copy
import time


INFINITY = 10 ** 6

EMPTY = 2
BLACK = 0
WHITE = 1

START_POSITION = [
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 1, 0, 2, 2, 2],
    [2, 2, 2, 0, 1, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2],
]

TRANSPOSITION_TABLE = {}


class Searcher:
    def __init__(self, evaluators, pieces=None, side=BLACK):
        """
        Searcher instance: an engine which finds the "best" move for the current
        board state.
        :param pieces: 2d list <- arrangement of pieces on the board
        :param side: side to play next
        """

        if pieces is None:
            pieces = START_POSITION

        self.fully_expanded = 0
        self.tree_depth = 0
        self.pieces = 4

        self.evaluators = evaluators
        self.board = reversi.Board(pieces, side)
        self.game_tree = anytree.Node(self.board, expand=True)

        self.caught_up = True

    def cut(self, node=None):
        """
        Prune the treee...
        :param node: the node to cut from
        :return: None
        """

        if node is None:
            node = self.game_tree

        if len(node.children) <= 2:
            print "Cut: ", len(node.children), "/", len(node.children)
            return

        try:
            maximum = max(node.children, key=lambda n: n.score).score
            minimum = min(node.children, key=lambda n: n.score).score
        except AttributeError:
            return

        if self.board.side + node.depth == BLACK:
            score_range = maximum - minimum  # 0 -> x
            score_cutoff = 0.5 * score_range + minimum
            cutoff_function = lambda s: s >= score_cutoff
            foo = min
        else:
            score_range = minimum - maximum  # x -> 0
            score_cutoff = 0.5 * score_range + maximum
            cutoff_function = lambda s: s <= score_cutoff
            foo = max

        good = filter(lambda n: cutoff_function(n.score), list(node.children))
        bad = filter(lambda n: not cutoff_function(n.score), list(node.children))
        while len(good) < 2:
            good.append(foo(bad, key=lambda n: n.score))

        print "Cut: ", len(good), "/", len(node.children)

        node.children = good

    @staticmethod
    def expand_node(node):
        """
        Expands a particular node by depth one.
        :param node: anytree.Node() <- the node to expand
        :return: None
        """

        for move in node.name.legal_moves_notation:
            new_board = copy.deepcopy(node.name)
            new_board.move(move)
            anytree.Node(new_board, parent=node, move=move, expand=True)

    def expand(self, t=INFINITY):
        """
        Increments 'self.fully_expanded', then expands the entire tree to a
        depth of 'self.fully_expanded' in the time alloted. If incomplete, just
        leaves as is.
        :param t: int <- time limit in seconds
        :return: None
        """

        stop_time = time.time() + t

        if self.caught_up:
            self.fully_expanded += 1
            self.tree_depth = max(self.tree_depth, self.fully_expanded)
            self.caught_up = False

        for node in anytree.LevelOrderIter(self.game_tree):
            if node.depth >= self.fully_expanded:
                break
            if time.time() > stop_time:
                return
            if node.expand and node.is_leaf:
                self.expand_node(node)

        self.caught_up = True

    def timed_expand(self, t):
        """
        Expands as much as possible in the time allotted.
        :param t: int <- time limit in seconds
        :return: None
        """

        end_time = time.time() + t

        while time.time() < end_time:
            if self.fully_expanded > 64 - self.pieces + 1:
                break

            if self.fully_expanded > 2:
                self.cut()

            starting_nodes = self.number_nodes()
            time1 = time.time()
            self.expand(end_time - time.time())
            self.update_scores()
            time2 = time.time()
            ending_nodes = self.number_nodes()

            expanded_nodes = ending_nodes - starting_nodes
            nodes_per_second = int(float(expanded_nodes) /
                                   (time2 - time1))

            print "{} ply ::".format(self.fully_expanded),
            print "expanded {} nodes @ {} nodes/sec".format(expanded_nodes,
                                                            nodes_per_second)

    def minimax(self, node, alpha=-INFINITY, beta=INFINITY):
        """
        Simple minimax algorithm with alpha-beta pruning.
        :param node: anytree.Node() <- the node to operate on
        :param alpha: int <- an alpha-beta parameter
        :param beta: int <- an alpha-beta parameter
        :return: None
        """

        if node.depth >= self.fully_expanded - int(not self.caught_up):
            if node.name in TRANSPOSITION_TABLE:
                node.score = TRANSPOSITION_TABLE[node.name]
            else:
                score = self.evaluators[self.board.side](node.name)
                TRANSPOSITION_TABLE[node.name] = score
                node.score = score
            return

        if (node.depth + self.board.side) % 2 == 0:
            value = -INFINITY
            for child in node.children:
                self.minimax(child, alpha, beta)
                value = max(value, child.score)
                alpha = max(alpha, value)
                if alpha > beta:
                    for child in node.children:
                        child.score = alpha
                    break
            node.score = value
        else:
            value = INFINITY
            for child in node.children:
                self.minimax(child, alpha, beta)
                value = min(value, child.score)
                beta = min(beta, value)
                if alpha > beta:
                    for child in node.children:
                        child.score = alpha
                    break
            node.score = value

    def update_scores(self):
        """
        Updates the scores on the tree.
        :return: None
        """

        while self.fully_expanded - int(not self.caught_up) < 1:
            self.expand()

        for child in self.game_tree.children:
            self.minimax(child, -INFINITY, INFINITY)

        if self.board.side == BLACK:
            self.game_tree.score = max(
                self.game_tree.children, key=lambda n: n.score if n.height == self.fully_expanded else -INFINITY
            ).score
        else:
            self.game_tree.score = min(
                self.game_tree.children, key=lambda n: n.score if n.height == self.fully_expanded else INFINITY
            ).score

    def best_move(self):
        """
        Find the move the engine thinks is best.
        :return: the "best" move in notation format -> (eg. "c4")
        """

        while self.fully_expanded - int(not self.caught_up) < 1:
            self.expand()
            self.update_scores()

        if self.board.side == BLACK:
            return max(self.game_tree.children, key=lambda c: c.score).move
        else:
            return min(self.game_tree.children, key=lambda c: c.score).move

    def move(self, notation):

        while self.fully_expanded - int(not self.caught_up) < 1:
            self.expand()
            self.update_scores()

        for child in self.game_tree.children:
            if child.move == notation:
                child.parent = None
                self.game_tree = child
                self.board.move(notation)

                self.fully_expanded -= 1
                self.tree_depth = self.game_tree.height
                self.pieces += 1

        for board in TRANSPOSITION_TABLE.keys():
            if len(board.available_positions) >= 64 - self.pieces:
                del TRANSPOSITION_TABLE[board]

        for node in anytree.PreOrderIter(self.game_tree):
            node.expand = True

    def number_nodes(self):
        return len(list(anytree.PreOrderIter(self.game_tree)))

    def display_tree(self):
        print anytree.RenderTree(self.game_tree)


if __name__ == "__main__":
    import evaluator_ab

    s = Searcher(evaluator_ab.evaluate)

    while not s.board.is_over():
        while s.number_nodes() < 1000 and s.fully_expanded < 50:
            s.expand()
            print "{} ply :: {} nodes".format(s.fully_expanded, s.number_nodes())

        s.update_scores()
        print s.best_move()
        s.move(s.best_move())
        s.board.display()
