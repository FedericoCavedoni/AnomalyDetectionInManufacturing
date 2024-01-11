import numpy as np
from sklearn.neural_network import MLPClassifier


class Classifier(MLPClassifier):
    def __init__(self):
        super(Classifier, self).__init__()
        self._test_error = None
        self._num_layers = None
        self._num_neurons = None
        self._validation_error = None
        self.early_stopping = False

    def set_num_neurons(self, num_neurons: int):
        self._num_neurons = num_neurons

    def get_num_neurons(self):
        return self._num_neurons

    def set_num_layers(self, num_layers: int):
        self._num_layers = num_layers

    def get_num_layers(self):
        return self._num_layers

    def set_num_iterations(self, num_iterations: int):
        self.max_iter = num_iterations

    def fit(self, x, y):
        self.hidden_layer_sizes = np.full((self._num_layers,), self._num_neurons, dtype=int)
        super().fit(x, y)

    def get_loss_curve(self):
        return self.loss_curve_

    def get_num_iterations(self):
        return self.max_iter

    def set_validation_error(self, validation_error: float):
        self._validation_error = validation_error

    def get_validation_error(self):
        return self._validation_error

    def get_training_error(self):
        return self.loss_

    def get_test_error(self):
        return self._test_error

    def get_train_valid_error_difference(self):
        if self.get_validation_error() == 0:
            return 1
        return (self.get_validation_error() - self.get_training_error()) / self.get_validation_error()

    def get_valid_test_error_difference(self):
        if self.get_test_error() == 0:
            return 1
        return (self.get_test_error() - self.get_validation_error()) / self.get_test_error()

    def classifier_report(self):
        return {'validation_error': self.get_validation_error(),
                'training_error': self.get_training_error(),
                'difference': self.get_train_valid_error_difference(),
                'num_layers': self.get_num_layers(),
                'num_neurons': self.get_num_neurons(),
                'network_complexity': self.get_num_layers() * self.get_num_neurons()
                }

    def set_test_error(self, test_error: float):
        self._test_error = test_error
