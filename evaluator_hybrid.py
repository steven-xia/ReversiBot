import evaluator_ab
import evaluator_nn


def evaluate(board):
    e1 = evaluator_ab.evaluate(board)
    e2 = evaluator_nn.evaluate(board)
    return float(e1 + 9 * e2) / 10

