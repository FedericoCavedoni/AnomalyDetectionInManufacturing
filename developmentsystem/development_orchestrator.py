import json
import os
import time
from threading import Thread

from utilities.utils import Utils

from developmentsystem.configuration_parameters import ConfigurationParameters
from testing.testing_orchestrator import TestingOrchestrator
from training.training_orchestrator import TrainingOrchestrator
from validation.validation_orchestrator import ValidationOrchestrator
from development_system_io import DevelopmentSysIO


class DevelopmentOrchestrator:
    def __init__(self, dev_sys_io: DevelopmentSysIO):
        self._dev_sys_io = dev_sys_io
        rest_server = Thread(target=dev_sys_io.listener)
        rest_server.setDaemon(True)
        rest_server.start()
        self._service_flag = ConfigurationParameters.SERVICE_FLAG

    def develop_classifier(self):
        while True:
            stop_and_go = None
            result_training_phase = 0
            # 'skip_learning_sets' is used to restart the process when, after validation, there is no valid
            # classifier (I skip the reception of the learning sets)
            skip_learning_sets = False
            if not self._service_flag and os.path.isfile("data/stop&go.json"):  # If we are in "STOP&GO" mode
                with open("data/stop&go.json", 'r') as f:  # Read the content of the file stop&go.json
                    stop_and_go = json.load(f)
                if (stop_and_go['human_task'] == "check_validation_results" and  # Human task: Check Validation Results
                        int(stop_and_go['human_choice']) == 0):  # No valid classifier
                    Utils.delete_files_pattern("/data/classifier*.sav")
                    stop_and_go = None  # Restart development
                    skip_learning_sets = True
            elif self._service_flag:  # Stop&Go is simplified and timestamps are sent to Service Class
                self._service_flag_orchestration()
                continue
            if stop_and_go is None:  # Start of development process OR Restart after no valid classifier from validation
                if not skip_learning_sets:  # If the development process is at the beginning --> Wait for learning sets
                    self._dev_sys_io.receive_learning_sets()
                    print("LEARNING SETS RECEIVED")
                training_orchestrator = TrainingOrchestrator()
                # Give the control of the application to the orchestrator of first training phase (to set #iterations)
                result_training_phase = training_orchestrator.train_classifier("start")
                if result_training_phase == -1:  # If Stop & Go is used, I need to stop the run to wait for human choice
                    return
            elif stop_and_go['human_task'] == "set_#iterations":
                training_orchestrator = TrainingOrchestrator()
                result_training_phase = training_orchestrator.train_classifier("set_#iterations", stop_and_go)
                if result_training_phase == -1:  # If Stop & Go is used, I need to stop the run to wait for human choice
                    return
            elif stop_and_go['human_task'] == "check_learning_plot":
                training_orchestrator = TrainingOrchestrator()
                result_training_phase = training_orchestrator.train_classifier("check_learning_plot", stop_and_go)
                if result_training_phase == -1:  # If Stop & Go is used, Stop the run to wait for human choice
                    return
            if result_training_phase > 0:  # result_training_phase contains the # iterations established
                # Training phase completed --> Start validation phase
                validation_orchestrator = ValidationOrchestrator()
                result_validation_phase = validation_orchestrator.validation(result_training_phase)
                if result_validation_phase == -1:  # If Stop & Go is used, Stop the run to wait for human choice
                    return
            elif stop_and_go['human_task'] == "check_validation_results":
                # If there is a valid classifier --> Choose it and test it
                test_orchestrator = TestingOrchestrator(stop_and_go['human_choice'])
                result_test_phase = test_orchestrator.test_classifier()
                if result_test_phase == -1:  # If Stop & Go is used, Stop the run to wait for human choice
                    return
            if stop_and_go['human_task'] == "check_test_results":
                if int(stop_and_go['human_choice']) == 0:  # Test not passed --> Send restart schemas
                    self._dev_sys_io.send_restart_configuration()
                    print("CONFIGURATION SENT")
                else:  # Test passed --> Send classifier to Production System for deployment
                    self._dev_sys_io.send_classifier()
                    print("CLASSIFIER SENT")
            os.remove("data/stop&go.json")

    def _service_flag_orchestration(self):
        self._dev_sys_io.receive_learning_sets()
        self._dev_sys_io.send_timestamp(time.time(), "start")
        print("LEARNING SETS RECEIVED")
        chosen_classifier = 0
        while chosen_classifier == 0:
            result_training_phase = TrainingOrchestrator().train_classifier("start")
            chosen_classifier = ValidationOrchestrator().validation(result_training_phase)
        result = TestingOrchestrator(chosen_classifier).test_classifier()
        self._dev_sys_io.send_timestamp(time.time(), "end")
        if result == 0:  # Test not passed --> Send restart schemas
            self._dev_sys_io.send_restart_configuration()
            print("CONFIGURATION SENT")
        else:  # Test passed --> Send classifier to Production System for deployment
            self._dev_sys_io.send_classifier()
            print("CLASSIFIER SENT")


if __name__ == '__main__':
    ConfigurationParameters.load_configuration()
    DevelopmentOrchestrator(DevelopmentSysIO.get_instance()).develop_classifier()
