import evaluator
import evaluator2


def evaluate(board):
    e1 = evaluator.evaluate(board)
    e2 = evaluator2.evaluate(board)
    return (e1 + e2) / 2

