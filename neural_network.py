#! /usr/bin/python

"""
Implementation of a simple Artificial Neural Network!

Features:
  - Flexible hidden layer sizes
  - Automatically adds a bias to all inputs
  - Implemented [leaky] ReLU for the non-linearity
  - Implemented Hinton's dropout
  - Implemented He weights initializer
  - Implemented Adam gradient descent optimizer.

Possible uses:
  - a simple (or not so simple) classifier
  - a neural network teaching/experimental tool

Dependencies:
  - numpy

"""

# Imports here...
import numpy

# Set CONSTANTS here...
TRAINING_INPUTS = numpy.array([[0, 0],
                               [0, 1],
                               [1, 0],
                               [1, 1]])
TRAINING_OUTPUTS = numpy.array([[0],
                                [1],
                                [1],
                                [0]])
INPUT_LAYER_SIZE = len(TRAINING_INPUTS[0])
OUTPUT_LAYER_SIZE = len(TRAINING_OUTPUTS[0])
HIDDEN_LAYER_SIZES = [8]

TRAINING_ITERATIONS = 100
TRAINING_ALPHA = 0.1
VERBOSE = 100

DROPOUT_PERCENTAGE = 0.2


# Classes here...
class NeuralNetwork:
    def __init__(self, input_layer_size=2, hidden_layer_sizes=(4,), output_layer_size=1):
        # Process class arguments.
        self.hidden_layer_sizes = hidden_layer_sizes

        # Seed the random number generator to make it pseudo-random.
        numpy.random.seed(0)

        # Create the weights.
        if len(hidden_layer_sizes) == 0:
            self.weights_list = [self.initialize_weights(input_layer_size + 1, output_layer_size)]
        else:
            self.weights_list = [self.initialize_weights(input_layer_size + 1, self.hidden_layer_sizes[0])]
            for hidden_layer_size_index in range(len(self.hidden_layer_sizes) - 1):
                input_weights = hidden_layer_sizes[hidden_layer_size_index]
                output_weights = hidden_layer_sizes[hidden_layer_size_index + 1]
                self.weights_list.append(self.initialize_weights(input_weights, output_weights))
            self.weights_list.append(self.initialize_weights(self.hidden_layer_sizes[-1], output_layer_size))

        self.iteration = 0
        self.means = [0] * len(self.weights_list)
        self.variances = [0] * len(self.weights_list)

    @staticmethod
    def initialize_weights(rows, columns):
        """
        Initializes weights randomly with (hopefully) a mean of zero.
        :param rows: the number of rows in the weights matrix
        :param columns: the number of columns in the weights matrix
        :return: the initialized weights
        """
        return numpy.random.randn(rows, columns) * numpy.sqrt(rows / 2.0)
        # return 2 * numpy.random.random((rows, columns)) - 1

    @staticmethod
    def _relu(x):
        return numpy.maximum(0.01 * x, x)

    @staticmethod
    def _relu_to_derivative(x):
        dx = numpy.ones_like(x)
        dx[x < 0] = 0.01
        return dx

    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + numpy.exp(-x))

    @staticmethod
    def _sigmoid_to_derivative(x):
        return x * (1 - x)

    def non_linearity(self, x, derivative=False, final_layer=False):
        numpy.clip(x, -700, 700, out=x)
        if final_layer:
            if derivative:
                return self._sigmoid_to_derivative(x)
            return self._sigmoid(x)
        else:
            if derivative:
                return self._relu_to_derivative(x)
            return self._relu(x)

    def sdg(self, layers, layers_deltas, alpha):
        for layer_index in reversed(xrange(len(layers) - 1)):
            self.weights_list[layer_index] += alpha * layers[layer_index].T.dot(layers_deltas[layer_index])

    def adam(self, layers, layers_deltas, alpha, beta1=0.9, beta2=0.999, epsilon=10 ** -8):
        self.iteration += 1

        for layer_index in reversed(xrange(len(layers) - 1)):
            gradient = layers[layer_index].T.dot(layers_deltas[layer_index])
            self.means[layer_index] = beta1 * self.means[layer_index] + (1 - beta1) * gradient
            self.variances[layer_index] = beta2 * self.variances[layer_index] + (1 - beta2) * (gradient ** 2)

            time_mean = self.means[layer_index] / (1 - beta1 ** self.iteration)
            time_variance = self.variances[layer_index] / (1 - beta2 ** self.iteration)

            self.weights_list[layer_index] += alpha * time_mean / \
                                              (numpy.sqrt(time_variance) + epsilon)
            # self.weights_list[layer_index] += alpha * gradient

    def train(self, training_inputs, training_outputs, iterations=1000, alpha=1.0, verbose=10 ** 6,
              dropout_percentage=0.2):
        # Add a bias...
        training_inputs = numpy.c_[training_inputs, numpy.ones(len(training_inputs))]
        for iteration in xrange(iterations + 1):
            # Forward propagate through the layers.
            layers = [training_inputs]
            for weights_set_index in xrange(len(self.weights_list) - 1):
                layers.append(self.non_linearity(numpy.dot(layers[-1], self.weights_list[weights_set_index])))
                dropout_matrix = numpy.random.binomial([numpy.ones((len(training_inputs),
                                                                    self.hidden_layer_sizes[weights_set_index]))],
                                                       1 - dropout_percentage)[0]
                layers[-1] *= dropout_matrix * (1.0 / (1 - dropout_percentage))

            layers.append(self.non_linearity(numpy.dot(layers[-1], self.weights_list[-1]), final_layer=True))

            # Backward propagate.
            layers_deltas = []
            layer_error = training_outputs - layers[-1]  # First layer is special...
            layers_deltas.insert(0, layer_error * self.non_linearity(layers[-1], final_layer=True))
            for layer_index in reversed(xrange(1, len(layers) - 1)):
                # Remainder errors dependant on last synapse weights...
                layer_error = layers_deltas[0].dot(self.weights_list[layer_index].T)
                layers_deltas.insert(0, layer_error * self.non_linearity(layers[layer_index]))

            # Apply the changes.
            # self.sdg(layers, layers_deltas, alpha)
            self.adam(layers, layers_deltas, alpha)

            if type(verbose) == bool and verbose:
                for input_question_index in xrange(len(layers[0])):
                    result = "CORRECT"
                    if map(int, layers[-1][input_question_index].round()) != TRAINING_OUTPUTS[input_question_index]:
                        result = "WRONG!"
                    print "IN{} -> OUT{} ~ {} :: {}".format(map(int, layers[0][input_question_index][:-1]),
                                                            layers[-1][input_question_index],
                                                            map(int, layers[-1][input_question_index].round()),
                                                            result)
            if iteration % verbose == 0:
                print "Iteration {}:".format(iteration)

                for input_question_index in xrange(len(layers[0])):
                    result = "CORRECT"
                    if map(int, layers[-1][input_question_index].round()) != TRAINING_OUTPUTS[input_question_index]:
                        result = "WRONG!"
                    print "    IN{} -> OUT{} ~ {} :: {}".format(map(int, layers[0][input_question_index][:-1]),
                                                                layers[-1][input_question_index],
                                                                map(int, layers[-1][input_question_index].round()),
                                                                result)

    def think(self, input_questions):
        input_layer = numpy.c_[input_questions, numpy.ones(len(input_questions))]

        layers = [input_layer]
        for weights_set_index in xrange(len(self.weights_list) - 1):
            layers.append(self.non_linearity(numpy.dot(layers[-1], self.weights_list[weights_set_index])))
        layers.append(self.non_linearity(numpy.dot(layers[-1], self.weights_list[-1]), final_layer=True))

        return layers[-1]


def _train(train_subject, training_inputs, training_outputs, iterations=1000, alpha=1, verbose=False):
    print "Training... "
    train_subject.train(training_inputs, training_outputs, iterations, alpha, verbose=verbose)


def _test(test_subject, testing_questions):
    print "Testing... "
    answers = test_subject.think(testing_questions)
    for testing_question_index in xrange(len(testing_questions)):
        print "IN{} -> OUT{}".format(testing_questions[testing_question_index],
                                     answers[testing_question_index],
                                     map(lambda l: map(int, l), answers.round())[0])


# The main part of the code...
if __name__ == "__main__":
    logic_gate = NeuralNetwork(INPUT_LAYER_SIZE, HIDDEN_LAYER_SIZES, OUTPUT_LAYER_SIZE)
    _train(logic_gate, TRAINING_INPUTS, TRAINING_OUTPUTS, iterations=TRAINING_ITERATIONS,
           alpha=TRAINING_ALPHA, verbose=VERBOSE)
    _test(logic_gate, TRAINING_INPUTS)
