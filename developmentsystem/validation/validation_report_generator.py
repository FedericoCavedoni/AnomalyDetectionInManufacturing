from typing import List

import joblib

from developmentsystem.training.classifier import Classifier
from developmentsystem.configuration_parameters import ConfigurationParameters


class ValidationReportGenerator:
    def __init__(self):
        self._top_5_classifiers = []

    def generate_validation_report(self, classifiers: List[Classifier]):  # It looks for the top 5 classifiers
        # Assuming at least 5 classifiers
        for i in range(1, 6):
            min_validation_error = -1
            top_classifier = None
            for classifier in classifiers:  # It looks for the classifier with the minimum validation error
                current_validation_error = classifier.get_validation_error()
                if min_validation_error == -1:
                    min_validation_error = current_validation_error
                    top_classifier = classifier
                elif min_validation_error > current_validation_error:
                    min_validation_error = current_validation_error
                    top_classifier = classifier
            classifier_report = {'index': i}
            classifier_report.update(top_classifier.classifier_report())
            self._top_5_classifiers.append(classifier_report)
            joblib.dump(top_classifier, "data/classifier" + str(i) + ".sav")
            classifiers.remove(top_classifier)
        validation_report = {'report': self._top_5_classifiers,
                             'overfitting_tolerance': ConfigurationParameters.OVERFITTING_TOLERANCE}
        return validation_report

    def get_top_5_classifiers(self):
        return self._top_5_classifiers
