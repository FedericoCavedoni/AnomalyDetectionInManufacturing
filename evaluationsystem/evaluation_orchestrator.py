"""
Module: evaluation_orchestrator.py
Author: Nicolò Salti

Classes:
    EvaluationOrchestrator: main class that represents the main logic of
    the evaluation system
"""
import json
import random
import time
from threading import Thread

from evaluationsystem.configuration_parameters import ConfigurationParameters
from evaluationsystem.evaluation_json_io import EvaluationJsonIO
from evaluationsystem.evaluation_report_view import EvaluationReportView
from evaluationsystem.label_storage_controller import LabelStorageController


class EvaluationOrchestrator:
    """
    This class represents the main logic of the evaluation system, it simulates
    everything related to the BPMN process EVALUATE CLASSIFIER PERFORMANCE
    """
    def __init__(self):
        """
        This is the constructor of the evaluation orchestrator, it initializes the
        configuration parameters, the class attributes and creates the table of the db
        """
        # Initialize configuration parameter
        ConfigurationParameters.initialize_config_params()
        # get references to other classes
        self.eval_sys_io = EvaluationJsonIO.get_instance()
        self.eval_report_view = EvaluationReportView()
        self.label_storage_controller = LabelStorageController("label.db")
        # Create the table if not exists
        self.label_storage_controller.create_label_table()
        self._service_flag = ConfigurationParameters.SERVICE_FLAG
        self._num_labels_classifier = 0
        self._num_labels_expert = 0

    def evaluate_classifier(self):
        """
        This method represents the behavior of the evaluation system, waits for labels from
        other system and when we have a sufficient number of labels, it generates the
        evaluation report. Subsequently, the human evaluates the report and, depending
        on the decision, it sends the restart to the service class
        :return:
        """
        # starting the flask server as a thread
        listener = Thread(target=self.eval_sys_io.listener,
                          args=(ConfigurationParameters.EVALUATION_IP,
                                ConfigurationParameters.EVALUATION_PORT))
        listener.setDaemon(True)
        listener.start()
        print("Evaluation system started")

        stop_and_go = None
        # if the service flag is false, the stop and go interaction pattern is used
        if not self._service_flag:
            with open("data/stop&go.json", 'r', encoding='utf_8') as stop_and_go_file:
                stop_and_go = json.load(stop_and_go_file)

        while True:
            if stop_and_go is None or stop_and_go["step"] == "before_evaluation":
                while True:
                    # wait until we have a sufficient number of labels
                    label = self.eval_sys_io.recv_label()
                    if self._service_flag:
                        self.eval_sys_io.send_timestamp(time.time(), "start")
                        # store the received label in a db
                    self.label_storage_controller.store_label(label)
                    print("label stored: " + str(label.to_dict()))
                    # increments the received label counter (depending on the label_type)
                    self._inc_num_labels(label)
                    # if the number of label if sufficient let's generate the evaluation report
                    if self._check_num_labels():
                        print("sufficient labels")
                        break
                    elif self._service_flag:
                        self.eval_sys_io.send_timestamp(time.time(), "end")

                # get all the labels previously stored
                classifier_labels, expert_labels = self.label_storage_controller.get_stored_labels(
                    2 * ConfigurationParameters.MIN_LABELS)

                # generate the evaluation report
                self.eval_report_view.generate_evaluation_report(classifier_labels, expert_labels)

                # remove stored labels
                self.label_storage_controller.remove_label(classifier_labels)
                self.label_storage_controller.remove_label(expert_labels)
                # decrease the label counters a value equal to the label used to generate the report
                self._num_labels_expert = (self._num_labels_expert
                                           - ConfigurationParameters.MIN_LABELS)
                self._num_labels_classifier = (self._num_labels_classifier
                                               - ConfigurationParameters.MIN_LABELS)
                print("labels removed")
                if not self._service_flag:
                    return
            # service flag is true, the decision is generated statistically
            if stop_and_go is None:
                index = int(random.random() <= 0.14)
                if index == 1:  # 14%
                    # classifier is good (both thresholds are satisfied)
                    print("Good classifier")
                    if self._service_flag:
                        self.eval_sys_io.send_timestamp(time.time(), "end")
                    continue
                else:  # 86%
                    # classifier is not good (one of the two threshold is not satisfied)
                    print("Bad classifier")
                    if self._service_flag:
                        self.eval_sys_io.send_timestamp(time.time(), "end")
                    self.eval_sys_io.send_restart_configuration()
                    print("restart configuration sent")
            elif stop_and_go["step"] == "classifier_evaluated":
                # human task: evaluate classifier
                decision = self.eval_sys_io.get_classifier_decision()
                if decision == "bad":
                    # the human decided the classifier is bad
                    print("Bad classifier")
                    # let the system wait for new labels when it restarts
                    stop_and_go["step"] = "before_evaluation"
                    with open("data/stop&go.json", 'w', encoding='utf_8') as stop_and_go_file:
                        json.dump({"step": "before_evaluation"}, stop_and_go_file)
                    if self._service_flag:
                        self.eval_sys_io.send_timestamp(time.time(), "end")
                    self.eval_sys_io.send_restart_configuration()
                    print("restart configuration sent")
                    continue
                elif decision == "good":
                    # the human decided the classifier is good
                    print("Good classifier")
                    # let the system wait for new labels when it restarts
                    stop_and_go["step"] = "before_evaluation"
                    with open("data/stop&go.json", 'w', encoding='utf_8') as stop_and_go_file:
                        json.dump({"step": "before_evaluation"}, stop_and_go_file)
                    continue
                if self._service_flag:
                    self.eval_sys_io.send_timestamp(time.time(), "end")

    # function to increase the label counter (depending on the label_type)
    def _inc_num_labels(self, label):
        if label.get_label_type() == 0:
            self._num_labels_classifier = self._num_labels_classifier + 1
        else:
            self._num_labels_expert = self._num_labels_expert + 1

    # function to check if the number of labels is sufficient to generate the report
    def _check_num_labels(self):
        return self._num_labels_expert >= ConfigurationParameters.MIN_LABELS and \
            self._num_labels_classifier >= ConfigurationParameters.MIN_LABELS


if __name__ == "__main__":
    evaluation_orchestrator = EvaluationOrchestrator()
    evaluation_orchestrator.evaluate_classifier()
