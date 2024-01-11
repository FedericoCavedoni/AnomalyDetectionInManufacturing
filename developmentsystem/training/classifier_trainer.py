import math
from numpy import ravel
from sklearn.metrics import log_loss
from pandas import read_csv

from developmentsystem.training.classifier import Classifier
from developmentsystem.configuration_parameters import ConfigurationParameters


class ClassifierTrainer:
    def __init__(self):
        self._classifier = Classifier()

    def train(self, validation: bool = False):
        training_data = read_csv('data/training_set.csv')
        training_labels = training_data['label']
        del training_data['label']
        # Train the classifier
        self._classifier.fit(x=training_data,
                             y=ravel(training_labels))
        if validation:
            self._validate()
        return self._classifier

    def _validate(self):
        validation_data = read_csv('data/validation_set.csv')
        validation_labels = validation_data['label']
        del validation_data['label']
        true_labels = []
        for label in validation_labels:
            if label == 1.0:
                true_labels.append([1.0, 0])
            else:
                true_labels.append([0, 1.0])
        validation_error = log_loss(y_true=true_labels,
                                    y_pred=self._classifier.predict_proba(validation_data))
        self._classifier.set_validation_error(validation_error)

    def set_average_hyperparameters(self):
        avg_neurons = math.ceil((ConfigurationParameters.MAX_NEURONS + ConfigurationParameters.MIN_NEURONS) / 2)
        avg_layers = math.ceil((ConfigurationParameters.MAX_LAYERS + ConfigurationParameters.MIN_LAYERS) / 2)
        self._classifier.set_num_neurons(avg_neurons)
        self._classifier.set_num_layers(avg_layers)

    def set_hyperparameters(self, num_layers: int, num_neurons: int):
        self._classifier.set_num_layers(num_layers)
        self._classifier.set_num_neurons(num_neurons)

    def set_num_iterations(self, num_iterations: int):
        self._classifier.set_num_iterations(num_iterations)
