"""
Module: evaluation_json_io.py
Author: Nicolò Salti

Classes:
    EvaluationJsonIO: class to manage communication with other modules
"""
import queue
import json
import jsonschema
import requests

from flask_restful import Resource, Api
from flask import Flask, request
from evaluationsystem.label import Label

app = Flask(__name__)
api = Api(app)


class EvaluationJsonIO(Resource):
    """
    This class is responsible for managing everything that concerns the communication with the
    other systems. It's a Flask server which expose a resource to receive labels. (It's
    implemented as a singleton class)
    """
    instance = None

    def __init__(self):
        """
        Constructor method used to initialize the class attributes, create a Queue object
        to store labels received from other systems
        """
        self._set_global_configuration()
        self._label_queue = queue.Queue()

        self._config_path = "configuration/eval_config_params.json"
        self._config_schema_path = "schemas/eval_config_schema.json"
        self._global_config_path = "../global_configuration.json"
        self._global_config_schema = "../global_configuration_schema.json"
        self._classifier_decision_path = "data/classifier_decision.json"
        self._classifier_decision_schema_path = "schemas/decision_schema.json"
        self._restart_config_path = "../development_system/configuration/restart_configuration.json"
        self._label_schema_path = "schemas/label_schema.json"

    @staticmethod
    def get_instance():
        """
        This method is responsible for getting the singleton instance of the EvaluationJsonIO class
        :return:
            EvaluationJsonIO.instance
        """
        if EvaluationJsonIO.instance is None:
            EvaluationJsonIO.instance = EvaluationJsonIO()

        return EvaluationJsonIO.instance


    def recv_label(self):
        """
        This method is used to get a label previously saved in the queue
        :return:
            Label: label object previously saved in the queue
        """
        return self._label_queue.get(block=True)

    def send_timestamp(self, timestamp, phase): # For testing purposes
        """
        This method is used to send a timestamp to the service class
        :param timestamp:
            Actual timestamp
        :param phase:
            Type of message to be sent ("start", "end")
        """
        endpoint = ("http://" + self._service_class_ip + ":"
        + str(self._service_class_port)
        + "/service/log_timestamp")
        message = {'system': 'Evaluation System', 'phase' : phase, 'timestamp': timestamp}
        requests.post(endpoint, json=message)

    def send_restart_configuration(self):
        """
        This method is used to send the restart configuration to the service class
        """
        endpoint = "http://" + self._msg_sys_ip + ':' + \
                    str(self._msg_sys_port) + "/service/messaging_system"
        restart_config = {"action" : "restart"}
        requests.post(endpoint, json=restart_config)

    def recv_config_params(self):
        """
        This method is used to simulate the reception of the configuration parameters.
        It reads from the configuration file the values
        :return:
            A tuple composed of: the parameters to initialize the parameters of the
            evaluation system, the parameters used to initialize ips and
            ports of the other system
        """
        with open(self._config_path, 'r', encoding='utf_8') as config_params:
            json_content = json.load(config_params)
        self._validate_json(json_content, self._config_schema_path)
        with open(self._global_config_path, 'r', encoding='utf_8') as global_config_params:
            global_json_content = json.load(global_config_params)
        self._validate_json(global_json_content, self._global_config_schema)
        return json_content, global_json_content

    def get_classifier_decision(self):
        """
        This method is used to obtain the decision of the human about the goodness
        of the classifier
        :return:
            str: decision about the goodness of the classifier
        """
        with open(self._classifier_decision_path, 'r', encoding='utf_8') as decision:
            json_content = json.load(decision)
        self._validate_json(json_content, self._classifier_decision_schema_path)
        return json_content['decision']

    def _validate_json(self, json_content, json_schema_path):
        """
        Utility function to validate a json
        :param
            json_content: content to be validated
        :param
            json_schema_path: path to the json schema
        """
        with open(json_schema_path, 'r', encoding='utf_8') as schema:
            json_schema = json.load(schema)
        jsonschema.validate(json_content, json_schema)

    def _set_global_configuration(self):
        """
        This private method is used to set the parameters related to
        ips and ports of the other systems
        """
        with open("../global_configuration.json", 'r', encoding='utf_8') as configuration:
            json_content = json.load(configuration)
        self._validate_json(json_content, "../global_configuration_schema.json")
        self._service_class_ip = json_content["Service Class"]["ip"]
        self._service_class_port = json_content["Service Class"]["port"]
        self._msg_sys_ip = json_content["Messaging System"]["ip"]
        self._msg_sys_port = json_content["Messaging System"]["port"]

    def _put_label_into_queue(self, label):
        """
        This private method is used to insert a label into the queue
        :param
            label: Label object to be inserted
        """
        self._label_queue.put(label)

    def listener(self, ip_address, port):
        """
        This method is called in the orchestrator to start the Flask server
        :param
            ip: of the Flask server
        :param
            port: of the Flask server
        """
        app.run(host=ip_address, port=port, debug=False, threaded=True)

    def post(self):
        """
        This method is used to handle post requests to the Flask server
        :return:
            The message to be sent as reply
        """
        json_content = request.get_json()
        # validation of the content received
        self._validate_json(json_content, self._label_schema_path)
        if json_content['sender'] == "expert":
            label_type = 1
        else:
            label_type = 0
        label = Label(json_content['uuid'], json_content['anomalous'], label_type)
        # add the label received in the queue
        EvaluationJsonIO.get_instance()._put_label_into_queue(label)
        return 'OK', 201


api.add_resource(EvaluationJsonIO, '/EvaluationSystem')
