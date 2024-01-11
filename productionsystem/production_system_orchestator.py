# pylint: disable=too-few-public-methods
# pylint: disable=line-too-long
# pylint: disable=import-error

"""
Module: production_system_orchestrator.py

This module contains the ProductionSystemOrchestrator class,
which orchestrates the main logic of the Production System.

Classes:
- ProductionSystemOrchestrator: Orchestrator class for the Production System.
"""

import time
from threading import Thread

from productionsystem.classifier_controller import ClassifierController
from productionsystem.configuration_parameters import ConfigurationParameters
from productionsystem.production_system_io import ProductionSystemIO


class ProductionSystemOrchestrator:
    """
    Orchestrator class for the Production System.

    This class manages the main logic of the Production System,
    including receiving and deploying classifiers,
    classifying prepared sessions, and handling the evaluation phase.

    Attributes:
    - _prod_sys_io (ProductionSystemIO): An instance of the ProductionSystemIO class for handling I/O functions.
    - _classifier_controller (ClassifierController): An instance of the ClassifierController class.
    - _service_flag (bool): Flag indicating the service status.
    - _evaluation_phase (bool): Flag indicating whether the system is in the evaluation phase.
    - _label_to_both_systems (int): Label to be sent to both systems.
    - _label_only_to_client (int): Label to be sent only to the client.
    """

    def __init__(self, prod_sys_io: ProductionSystemIO):
        """
        Constructor function for the ProductionSystemOrchestrator class.

        Parameters:
        - prod_sys_io (ProductionSystemIO): An instance of the ProductionSystemIO class for handling I/O functions.
        """
        self._prod_sys_io = prod_sys_io

        # Thread function to start the I/O functions
        rest_server = Thread(target=prod_sys_io.listener)
        rest_server.setDaemon(True)
        rest_server.start()

        self._classifier_controller = ClassifierController()
        self._service_flag = ConfigurationParameters.service_flag

        # Value to check the evaluation phase of the system
        self._evaluation_phase = False
        # Number of labels to be sent to the evaluation phase
        self._label_to_both_systems = ConfigurationParameters.label_to_both_systems
        # Number of session to be sent to the client only
        self._label_only_to_client = ConfigurationParameters.label_only_to_client

    def production(self):
        """
        Main function for the Production System.

        This function contains the main logic of the Production System, including receiving and deploying classifiers,
        classifying prepared sessions, and handling the evaluation phase.
        """
        session_sent = 0
        session_evaluated = 0

        while True:
            # Data received
            (result, data) = self._prod_sys_io.receive()

            if self._service_flag:
                print("Send 'Start' to Service Class")
                self._prod_sys_io.send_timestamp(time.time(), "start")

            # Deploy classifier signal received, classifier model received from Development System
            if result == "deploy":
                print("Classifier received")
                classifier = data
                ClassifierController.deploy(classifier)
                if self._service_flag:
                    print("Send 'End' to Service Class")
                    self._prod_sys_io.send_timestamp(time.time(), "end")

                print("Send 'Start Production' to Messaging System")
                self._prod_sys_io.send_start_prod_configuration()

            # Classify signal received, prepared session received from the Preparation System
            elif result == "classify":
                print("Prepared Session received")
                prepared_session = data
                label = self._classifier_controller.classify(prepared_session)

                # If evaluation phase is true, the label is also sent to the Evaluation System
                if self._evaluation_phase:
                    print("Label sent to Evaluation System")
                    self._prod_sys_io.send_label_to_eval_sys(label)
                if self._service_flag:
                    print("Send 'End' to Service Class")
                    self._prod_sys_io.send_timestamp(time.time(), "end")

                # The label is sent to the Client
                print("Label sent to Client")
                self._prod_sys_io.send_label_to_client(label)

                # Evaluation phase logic:
                # We send labels to Client until we reach the number '_label_only_to_client'
                # Then we send the number '_label_to_both_systems' to both Client and Evaluation System
                if self._evaluation_phase:
                    session_evaluated += 1
                    if session_evaluated == self._label_to_both_systems:
                        session_evaluated = 0
                        self._evaluation_phase = False
                else:
                    session_sent += 1
                    if session_sent == self._label_only_to_client:
                        session_evaluated = 0
                        session_sent = 0
                        self._evaluation_phase = True


if __name__ == '__main__':
    # get configuration params
    ConfigurationParameters.get_config_param()

    # start the Production System
    ProductionSystemOrchestrator(ProductionSystemIO.get_instance()).production()
