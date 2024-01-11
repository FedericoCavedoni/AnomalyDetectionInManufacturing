# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes
# pylint: disable=protected-access

"""
Module: production_system_io.py

This module contains the ProductionSystemIO class,
which manages I/O functions for the Production System.

Classes:
- ProductionSystemIO: Class for handling I/O functions of the Production System.
"""

import json
import queue
import jsonschema
import pandas as pd
import requests
from flask import Flask, request
from flask_restful import Resource, Api

from preparationsystem.prepared_session import PreparedSession

# Variables to manage the Flask server
app = Flask(__name__)
api = Api(app)


class ProductionSystemIO(Resource):
    """
    Class to manage I/O functions for the Production System.

    This class handles receiving messages from other systems, sending labels to the Evaluation System
    and Client, and managing the Flask server for Production System I/O.

    Attributes:
    - _instance (ProductionSystemIO): An instance of the ProductionSystemIO class.
    """

    _instance = None

    @staticmethod
    def get_instance():
        """
        Get an instance of the ProductionSystemIO class.

        Returns:
        ProductionSystemIO: An instance of the ProductionSystemIO class.
        """
        if ProductionSystemIO._instance is None:
            ProductionSystemIO._instance = ProductionSystemIO()
        return ProductionSystemIO._instance

    def __init__(self):
        """
        Constructor function for the ProductionSystemIO class.

        This function initializes the queue, file paths, and global configurations.
        """
        self._queue = queue.Queue()
        self._prepared_session_schema_path = "schemas/prepared_session_schema.json"
        self._config_schema_path = "schemas/configParamSchema.json"
        self._config_path = "configuration/configParam.json"
        self._set_global_configuration()

    def listener(self):
        """
        Start the Flask server for receiving messages.

        This function starts the Flask server to listen for incoming messages.
        """
        app.run(host=self._prod_sys_ip, port=self._prod_sys_port, debug=False, threaded=True)

    def post(self):
        """
        Post function to handle received messages.

        This function handles messages received by the Flask server.
        """
        try:
            if 'classifier' in request.files:
                self.get_instance()._queue.put(request.files['classifier'].stream.read())
                return {'answer': 'ok'}, 201
            message = request.get_json()
            if message['content'] == "prepared_session":
                self._validate_json(message, self._prepared_session_schema_path)
                self.get_instance()._queue.put(message)
                return {'answer': 'ok'}, 201

            return {'answer': 'wrong_content'}, 403

        except ValueError:
            return {'answer': 'error_invalid_json'}, 403

    @staticmethod
    def _receive_prepared_session(prepared_session_json):
        """
        Convert a JSON representation of a Prepared Session to a PreparedSession object.

        Parameters:
        - prepared_session_json (dict): JSON representation of a Prepared Session.

        Returns:
        PreparedSession: A PreparedSession object.
        """
        features = {
            'maximum_powerconsumptiontimeseries': [prepared_session_json['max_power_consumption']],
            'median_powerconsumptiontimeseries': [prepared_session_json['median_power_consumption']],
            'skeweness_powerconsumptiontimeseries': [prepared_session_json['skewness_power_consumption']],
            'meanabsolutedeviation_powerconsumptiontimeseries': [
                prepared_session_json['mean_absolute_deviation_consumption']],
            'tissue_product': [prepared_session_json['tissue_product']],
            'load_and_speed_type': [prepared_session_json['load_and_speed_type']]
        }
        features = pd.DataFrame(features)
        return PreparedSession(prepared_session_json['uuid'], features, prepared_session_json['label'])

    def receive(self):
        """
        Receive messages and distinguish between deploy and classification signals.

        Returns:
        tuple: A tuple containing the signal type ("deploy" or "classify") and the corresponding message.
        """
        message = self.get_instance()._queue.get(block=True)
        if isinstance(message, bytes):
            return "deploy", message

        return "classify", self._receive_prepared_session(message)

    def send_label_to_eval_sys(self, label):
        """
        Send a label to the Evaluation System.

        Parameters:
        - label (Label): The Label object to be sent.
        """
        endpoint = "http://" + self._ev_sys_ip + ":" + str(self._ev_sys_port) + "/EvaluationSystem"
        message = {'uuid': label.get_uuid(),
                   'anomalous': label.get_anomalous(),
                   'sender': 'classifier'}
        requests.post(endpoint, json=message, timeout=None)

    def send_label_to_client(self, label):
        """
        Send a label to the Client.

        Parameters:
        - label (Label): The Label object to be sent.
        """
        endpoint = "http://" + self._service_class_ip + ":" + str(self._service_class_port) + "/service/client"
        message = {'uuid': label.get_uuid(),
                   'anomalous': label.get_anomalous(),
                   'sender': 'classifier'}
        requests.post(endpoint, json=message, timeout=None)

    def send_timestamp(self, timestamp, phase):
        """
        Send a timestamp to the Service Class.

        Parameters:
        - timestamp (str): The timestamp to be sent.
        - phase (str): The phase of the production system.
        """
        endpoint = "http://" + self._service_class_ip + ":" + str(self._service_class_port) + "/service/log_timestamp"
        message = {'system': 'Production System', 'phase': phase, 'timestamp': timestamp}
        requests.post(endpoint, json=message, timeout=None)

    def send_start_prod_configuration(self):
        """
        Send the 'start production' signal to the Messaging System.
        """
        endpoint = "http://" + self._msg_sys_ip + ":" + str(self._msg_sys_port) + "/service/messaging_system"
        start_config = {'action': 'start production'}
        requests.post(endpoint, json=start_config, timeout=None)

    def get_initial_configuration(self):
        """
        Get the initial configuration from the 'configParam.json' file.

        Returns:
        dict: Configuration parameters retrieved from the production system.
        """
        with open(self._config_path, 'r', encoding='utf-8') as configuration:
            json_content = json.load(configuration)
        self._validate_json(json_content, self._config_schema_path)
        return json_content

    def _set_global_configuration(self):
        """
        Set global configuration parameters from the 'global_configuration.json' file.
        """
        global_path = "../global_configuration.json"
        with open(global_path, 'r', encoding='utf-8') as configuration:
            json_content = json.load(configuration)
        self._validate_json(json_content, "../global_configuration_schema.json")
        self._service_class_ip = json_content["Service Class"]["ip"]
        self._service_class_port = json_content["Service Class"]["port"]
        self._msg_sys_ip = json_content["Messaging System"]["ip"]
        self._msg_sys_port = json_content["Messaging System"]["port"]
        self._prod_sys_ip = json_content["Production System"]["ip"]
        self._prod_sys_port = json_content["Production System"]["port"]
        self._ev_sys_ip = json_content["Evaluation System"]["ip"]
        self._ev_sys_port = json_content["Evaluation System"]["port"]

    @staticmethod
    def _validate_json(json_content, json_schema_path):
        """
        Validate a JSON file against its schema.

        Parameters:
        - json_content (dict): The JSON content to be validated.
        - json_schema_path (str): The path to the JSON schema file.
        """
        with open(json_schema_path, 'r', encoding='utf-8') as schema:
            json_schema = json.load(schema)
        jsonschema.validate(json_content, json_schema)


# Add Flask resources to send messages
api.add_resource(ProductionSystemIO, "/ProductionSystem")
