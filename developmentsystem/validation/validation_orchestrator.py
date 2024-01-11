import copy
import itertools
import json
import os
import random

from developmentsystem.validation.validation_report_generator import ValidationReportGenerator
from developmentsystem.configuration_parameters import ConfigurationParameters
from developmentsystem.training.training_orchestrator import ClassifierTrainer


class ValidationOrchestrator:
    def __init__(self):
        self._service_flag: bool = ConfigurationParameters.SERVICE_FLAG
        self._classifiers = []
        self._validation_report = None

    def validation(self, num_iterations: int):  # It performs the grid search and generates the validation report
        # Grid Search
        classifier_trainer = ClassifierTrainer()
        classifier_trainer.set_num_iterations(num_iterations)
        # Compute all possible combinations of hyperparameters
        layers = []
        for i in range(ConfigurationParameters.MIN_LAYERS, ConfigurationParameters.MAX_LAYERS + 1,
                       ConfigurationParameters.STEP_LAYERS):
            layers.append(i)
        neurons = []
        for i in range(ConfigurationParameters.MIN_NEURONS, ConfigurationParameters.MAX_NEURONS + 1,
                       ConfigurationParameters.STEP_NEURONS):
            neurons.append(i)
        grid_search = list(itertools.product(layers, neurons))
        for (num_layers, num_neurons) in grid_search:
            print("SET HYPERPARAMETERS (layers, neurons): " + str((num_layers, num_neurons)))
            classifier_trainer.set_hyperparameters(num_layers, num_neurons)
            print("TRAIN")
            classifier = classifier_trainer.train(validation=True)
            self._classifiers.append(copy.deepcopy(classifier))
        # Generate validation report
        print("GENERATE VALIDATION REPORT")
        self._validation_report = ValidationReportGenerator().generate_validation_report(self._classifiers)
        check_validation_results = {'human_task': 'check_validation_results',
                                    'validation_report': self._validation_report,
                                    'human_choice': 'index_of_the_best_classifier_OR_0(string)'
                                    }
        with open('data/stop&go.json', 'w') as f:
            json.dump(check_validation_results, f)
        if not self._service_flag:
            print("CHECK VALIDATION RESULTS (HUMAN TASK)")
            return -1
        try:
            os.remove('data/validation_report.json')
        except OSError:
            pass
        os.rename('data/stop&go.json', 'data/validation_report.json')
        index = int(random.random() <= 0.95)
        if index == 0:  # 5%
            msg = "NO VALID CLASSIFIER"
        else:  # 95%
            index = random.randint(1, 5)
            msg = index
        print("CHECK VALIDATION RESULTS (STATISTICALLY GENERATED: " + str(msg) + ")")
        return index
