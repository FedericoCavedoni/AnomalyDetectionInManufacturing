from developmentsystem.configuration_parameters import ConfigurationParameters
from developmentsystem.training.classifier import Classifier


class TestReportGenerator:
    def __init__(self):
        pass

    def generate_test_report(self, classifier: Classifier):
        return {'generalization_tolerance': ConfigurationParameters.TEST_ERROR_TOLERANCE,
                'validation_error': classifier.get_validation_error(),
                'test_error': classifier.get_test_error(),
                'difference': classifier.get_valid_test_error_difference()}
