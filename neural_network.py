#! /usr/bin/python

"""
file: neural_network.py  -- version 0.5
Description: Implementation of a simple Artificial Neural Network!
Features:
  - Flexible hidden layer sizes
  - Automatically adds a bias to all inputs
  - Implemented ReLU for the non-linearity
  - Implemented Hinton's dropout
  - Implemented He weights initializer
  - Implemented momentum optimizer
Dependencies:
  - numpy
"""

# Imports here...
import numpy


# Classes here...
class NeuralNetwork:
    def __init__(self, input_layer_size=2, hidden_layer_sizes=(4,), output_layer_size=1):
        # Process class arguments.
        self.hidden_layer_sizes = hidden_layer_sizes

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
        self.velocities = [numpy.zeros_like(weights) for weights in self.weights_list]
        self.error = None

    @staticmethod
    def initialize_weights(rows, columns):
        """
        Initializes weights randomly with (hopefully) a mean of zero.
        :param rows: the number of rows in the weights matrix
        :param columns: the number of columns in the weights matrix
        :return: the initialized weights
        """

        return numpy.random.randn(rows, columns) * numpy.sqrt(2.0 / rows)

    @staticmethod
    def _relu(x):
        return numpy.maximum(0., x)

    @staticmethod
    def _relu_to_derivative(x):
        dx = numpy.ones_like(x)
        dx[x < 0] = 0.
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
            gradient = layers[layer_index].T.dot(layers_deltas[layer_index])
            self.weights_list[layer_index] += alpha * gradient

    def momentum(self, layers, layers_deltas, alpha, beta=0.9, ladba=0.01):
        for layer_index in reversed(xrange(len(layers) - 1)):
            gradient = layers[layer_index].T.dot(layers_deltas[layer_index])
            gradient = beta * self.velocities[layer_index] + gradient
            self.velocities[layer_index] = gradient
            self.weights_list[layer_index] += alpha * gradient

    def train(self, training_inputs, training_outputs, iterations=1000, alpha=1.0, beta=0.9, ladba=0.001,
              dropout_percentage=0.2):
        # Add a bias...
        training_inputs = numpy.c_[training_inputs, numpy.ones(len(training_inputs))]
        total_error = 0

        for iteration in xrange(1, iterations + 1):

            # Forward propagate through the layers.
            layers = [training_inputs]
            for weights_set_index in xrange(len(self.weights_list) - 1):
                layers.append(self.non_linearity(numpy.dot(layers[-1], self.weights_list[weights_set_index])))
                dropout_matrix = numpy.random.binomial([numpy.ones((len(training_inputs),
                                                                    self.hidden_layer_sizes[weights_set_index]))],
                                                       1 - dropout_percentage)[0]
                layers[-1] *= dropout_matrix * (1.0 / (1 - dropout_percentage))
                layers[-1] = numpy.nan_to_num(layers[-1])
            layers.append(self.non_linearity(numpy.dot(layers[-1], self.weights_list[-1]), final_layer=True))

            # Backward propagate.
            layers_deltas = []

            temp1 = numpy.ones_like(training_outputs)
            temp2 = numpy.ones_like(temp1)
            temp1[training_outputs < 0.5] = -1
            temp2[layers[-1] < 0.5] = -1
            temp3 = temp1 * temp2

            output_layer_error = training_outputs - layers[-1]  # First layer is special...

            temp = numpy.ones_like(output_layer_error)
            temp[output_layer_error < 0] = -1

            output_layer_error *= temp
            output_layer_error[temp3 < 0] **= 0.5
            output_layer_error *= temp

            # if alpha == 0:
            #     total_error += 100 * (1 - numpy.sum(numpy.abs(output_layer_error)) / len(training_outputs))
            #     break

            layers_deltas.insert(0, output_layer_error * self.non_linearity(layers[-1], final_layer=True))
            for layer_index in reversed(xrange(1, len(layers) - 1)):
                # Remainder errors dependant on last synapse weights...
                layer_error = layers_deltas[0].dot(self.weights_list[layer_index].T)
                layers_deltas.insert(0, layer_error * self.non_linearity(layers[layer_index]))

            # Apply the changes.
            self.iteration += 1
            # self.sdg(layers, layers_deltas, alpha)
            self.momentum(layers, layers_deltas, alpha, beta, ladba)

            total_error += 100 * (1 - numpy.sum(numpy.abs(output_layer_error)) / len(training_outputs))

        average_error = total_error / iterations
        if self.error is None:
            self.error = average_error
        else:
            self.error = 0.999 * self.error + 0.001 * average_error

        return total_error / iterations

    def think(self, input_questions):

        input_layer = numpy.c_[input_questions, numpy.ones(len(input_questions))]
        layers = [input_layer]
        for weights_set_index in xrange(len(self.weights_list) - 1):
            layers.append(numpy.nan_to_num(
                self.non_linearity(numpy.dot(layers[-1], self.weights_list[weights_set_index]))
            ))

        layers.append(self.non_linearity(numpy.dot(layers[-1], self.weights_list[-1]), final_layer=True))
        return layers[-1]
