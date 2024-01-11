import json
import queue

import pandas as pd

import jsonschema
import requests

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class DevelopmentSysIO(Resource):  # This class follows the Singleton Pattern
    _instance = None  # Static ("private") instance

    @staticmethod
    def get_instance():  # Static method to retrieve the instance of the class
        if DevelopmentSysIO._instance is None:
            DevelopmentSysIO._instance = DevelopmentSysIO()
        return DevelopmentSysIO._instance

    def __init__(self):
        self._queue = queue.Queue()  # The queue is used to store the received messages
        self._config_path = "configuration/development_system_configuration.json"
        self._config_schema_path = "schemas/dev_config_schema.json"
        self._learningsets_schema_path = "schemas/learningsets_schema.json"
        self._training_set_path = "data/training_set.csv"
        self._validation_set_path = "data/validation_set.csv"
        self._test_set_path = "data/test_set.csv"
        self._classifier_path = "data/classifier.sav"
        self._set_global_configuration()

    def listener(self):
        # Start REST Flask server
        app.run(host=self._dev_sys_ip, port=self._dev_sys_port, debug=False, threaded=True)

    def post(self):  # This method is called when HTTP POST is received
        message = request.get_json()
        try:
            if message['content'] == "learning_sets":  # learning sets received
                self._validate_json(message, self._learningsets_schema_path)
                DevelopmentSysIO.get_instance()._queue.put(message)
                return {'answer': 'ok'}, 201
            return {'answer': 'wrong_content'}, 403
        except ValueError:
            return {'answer': 'error_invalid_json'}, 403

    def receive_learning_sets(self):  # Extract from queue and save learning sets
        learning_sets_json = DevelopmentSysIO.get_instance()._queue.get(block=True)
        # From json array to csv file for each set
        pd.DataFrame.from_records(learning_sets_json['training_set']).to_csv(self._training_set_path, index=False)
        pd.DataFrame.from_records(learning_sets_json['validation_set']).to_csv(self._validation_set_path, index=False)
        pd.DataFrame.from_records(learning_sets_json['test_set']).to_csv(self._test_set_path, index=False)

    def send_classifier(self):  # Send the developed classifier to the Production System
        endpoint = "http://" + self._prod_sys_ip + ":" + str(self._prod_sys_port) + "/ProductionSystem"
        with open(self._classifier_path, "rb") as f:
            reply = requests.post(endpoint, files={'classifier': f}).json()
        if reply['answer'] != 'ok':
            print("Error while sending classifier to Production System for deployment")

    def send_restart_configuration(self):  # Send restart configuration to the Production System
        endpoint = "http://" + self._msg_sys_ip + ":" + str(self._msg_sys_port) + "/service/messaging_system"
        restart_config = {"action": "restart"}
        requests.post(endpoint, json=restart_config)

    def send_timestamp(self, timestamp: float, phase: str):  # For testing purposes
        endpoint = "http://" + self._service_class_ip + ":" + str(self._service_class_port) + "/service/log_timestamp"
        message = {'system': 'Development System', 'phase': phase, 'timestamp': timestamp}
        requests.post(endpoint, json=message)

    def get_initial_configuration(self):
        with open(self._config_path, 'r') as configuration:
            json_content = json.load(configuration)
        self._validate_json(json_content, self._config_schema_path)
        return json_content

    def _set_global_configuration(self):
        with open("../global_configuration.json", 'r') as configuration:
            json_content = json.load(configuration)
        self._validate_json(json_content, "../global_configuration_schema.json")
        self._service_class_ip: str = json_content["Service Class"]["ip"]
        self._service_class_port: int = json_content["Service Class"]["port"]
        self._msg_sys_ip: str = json_content["Messaging System"]["ip"]
        self._msg_sys_port: int = json_content["Messaging System"]["port"]
        self._dev_sys_ip: str = json_content["Development System"]["ip"]
        self._dev_sys_port: int = json_content["Development System"]["port"]
        self._prod_sys_ip: str = json_content["Production System"]["ip"]
        self._prod_sys_port: int = json_content["Production System"]["port"]

    def _validate_json(self, json_content: dict, json_schema_path: str):
        with open(json_schema_path, 'r') as schema:
            json_schema = json.load(schema)
        jsonschema.validate(json_content, json_schema)


api.add_resource(DevelopmentSysIO, "/DevelopmentSystem")
