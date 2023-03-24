import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(x))

class NeuralNetwork:
    def __init__(self, layers) -> None:

        self.weights = []

        for a, b in zip(layers[1:], layers[:-1]):
            self.weights.append(np.random.randn(b, a) / b)
        
        self.bias = []
        for a in layers[1:]:
            self.bias.append(np.random.randn(a))

    def forward(self, x):
        x = np.asarray(x)
        for weights, bias in zip(self.weights, self.bias):
            x = sigmoid(x.dot(weights) + bias)
        return x
