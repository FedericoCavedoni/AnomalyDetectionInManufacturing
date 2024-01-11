"""
Module: evaluation_report_view.py
Author: Nicolò Salti

Classes:
    EvaluationReportView: Class used to display evaluation report
"""
import json

from evaluationsystem.configuration_parameters import ConfigurationParameters
from evaluationsystem.evaluation_report import EvaluationReport


class EvaluationReportView:
    """
    Class used to handle the representation of the evaluation report
    """
    def __init__(self):
        """
        Constructor which initialize the number of evaluation report genereted
        since the beginning of the session
        """
        self.report_counter = 0

    def generate_evaluation_report(self, classifier_labels, expert_labels):
        """
        Method used to generate the evaluation report, which is stored as a json file
        :param
            classifier_labels: list of labels classified by the classifier
        :param
            expert_labels: list of labels classified by the expert
        :return:
            total_errors: number of errors of the evaluation report
            consecutive_errors: consecutive number of errors of the evaluation report
        """
        # compute the total error of the current evaluation
        total_errors = self._compute_total_errors(classifier_labels, expert_labels)
        # compute the maximum consecutive errors of the current evaluation
        consecutive_errors = self._compute_consecutive_errors(classifier_labels, expert_labels)
        self.report_counter = self.report_counter + 1
        max_errors = ConfigurationParameters.MAX_ERRORS
        max_consecutive_errors = ConfigurationParameters.MAX_CONSECUTIVE_ERRORS
        classifier_labels_dict = list()
        expert_labels_dict = list()
        for i in range(ConfigurationParameters.MIN_LABELS):
            classifier_labels_dict.append(classifier_labels[i].to_dict())
            expert_labels_dict.append(expert_labels[i].to_dict())
        # generate the evaluation report
        eval_report = EvaluationReport(expert_labels_dict, classifier_labels_dict,
                                       total_errors, consecutive_errors,
                                       max_errors, max_consecutive_errors)
        print("Evaluation report generated")
        eval_report_dict = eval_report.to_dict()
        eval_report_json = {
            "total_errors": eval_report_dict["total_errors"],
            "consecutive_errors": eval_report_dict["consecutive_errors"],
            "max_errors": eval_report_dict["max_errors"],
            "max_consecutive_errors": eval_report_dict["max_consecutive_errors"],
            "table": list()
        }
        for i in range(ConfigurationParameters.MIN_LABELS):
            eval_report_json["table"].append({
                "uuid": classifier_labels[i].get_uuid(),
                "expert_label": expert_labels[i].get_anomalous(),
                "classifier_label": classifier_labels[i].get_anomalous()
            })
        # save the evaluation report
        with open("data/reports/report" + str(self.report_counter) + ".json",
                  'w', encoding='utf_8') as report_file:
            json.dump(eval_report_json, report_file)

        return total_errors, consecutive_errors

    def _compute_total_errors(self, classifier_labels, expert_labels):
        """
        Private method to compute the total number of errors of the evaluation report
        :param
            classifier_labels: list of classifier labels
        :param
            expert_labels: list of expert labels
        :return:
            total_errors: total number of errors
        """
        # questo metodo deve ricevere i due array odinati per uuid
        total_errors = 0
        for classifier_label, expert_label in zip(classifier_labels, expert_labels):
            if classifier_label.get_anomalous() != expert_label.get_anomalous():
                total_errors = total_errors + 1

        return total_errors

    def _compute_consecutive_errors(self, classifier_labels, expert_labels):
        """
        Private method to compute the maximum number of consecutive errors of the evaluation report
        :param
            classifier_labels: list of classifier labels
        :param
            expert_labels: list of expert labels
        :return:
            max_consecutive_errors: maximum number of consecutive errors
        """
        consecutive_errors = 0
        max_consecutive_errors = 0
        for classifier_label, expert_label in zip(classifier_labels, expert_labels):
            if classifier_label.get_anomalous() != expert_label.get_anomalous():
                consecutive_errors = consecutive_errors + 1
                max_consecutive_errors = max(consecutive_errors, max_consecutive_errors)
            else:
                consecutive_errors = 0

        return max_consecutive_errors
