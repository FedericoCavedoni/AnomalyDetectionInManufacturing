"""
Module: evaluation_report.py
Author: Nicolò Salti

Classes:
    EvaluationReport: model class to represent the evaluation orchestrator
"""


class EvaluationReport:
    """
    Class that represent the model of the EvaluationReport
    """
    def __init__(self, expert_labels, classifier_labels, total_errors,
                 consecutive_errors, max_errors, max_consecutive_errors):
        """
        Constructor of the EvaluationReport
        :param
            expert_labels: list of labels classified by the expert
        :param
            classifier_labels: list of labels classified by the classifier
        :param
            total_errors: number of errors computed during evaluation process
        :param
            consecutive_errors: maximum number of consecutive errors computed
            during evaluation process
        :param
            max_errors: maximum number of errors allowed
        :param
            max_consecutive_errors: maximum number of consecutive errors allowed
        """
        self._expert_labels = expert_labels
        self._classifier_labels = classifier_labels
        self._total_errors = total_errors
        self._consecutive_errors = consecutive_errors
        self._max_errors = max_errors
        self._max_consecutive_errors = max_consecutive_errors

    def get_expert_labels(self):
        """
        :return:
            List of labels classified by the expert
        """
        return self._expert_labels

    def get_classifier_labels(self):
        """
        :return:
            List of labels classified by the classifier
        """
        return self._classifier_labels

    def get_total_erros(self):
        """
        :return:
            _total_errors: number of errors
        """
        return self._total_errors

    def get_consecutive_errors(self):
        """
        :return:
            _consecutive_errors: maximum number of consecutive errors
        """
        return self._consecutive_errors

    def get_max_errors(self):
        """
        :return:
            _max_errors: maximum number of errors allowed
        """
        return self._max_errors

    def get_max_consecutive_errors(self):
        """
        :return:
            _max_consecutive_errors: maximum number of consecutive errors allowed
        """
        return self._max_consecutive_errors

    def to_dict(self):
        """
        :return:
            A dictionary representing the evaluation report
        """
        return {
            'expert_labels': self._expert_labels,
            'classifier_labels': self._classifier_labels,
            'total_errors': self._total_errors,
            'consecutive_errors': self._consecutive_errors,
            'max_errors': self._max_errors,
            'max_consecutive_errors': self._max_consecutive_errors
        }
