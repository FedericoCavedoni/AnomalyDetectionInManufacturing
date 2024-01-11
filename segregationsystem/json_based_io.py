import json
import queue
import jsonschema
import requests

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class JsonBasedIO(Resource):
    instance = None

    def __init__(self):
        self._json_queue = queue.Queue()
        self._set_global_configuration()

    @staticmethod
    def get_instance():
        if JsonBasedIO.instance is None:
            JsonBasedIO.instance = JsonBasedIO()

        return JsonBasedIO.instance

    # prepared sessions queue used to receive msg from preparation system
    def put_json_into_queue(self, received_json):
        self._json_queue.put(received_json)

    def validate_json(self, json_content, json_schema_path):
        with open(json_schema_path, 'r') as schema:
            json_schema = json.load(schema)
        jsonschema.validate(json_content, json_schema)

    def listener(self):
        app.run(host=self._segr_sys_ip, port=self._segr_sys_port, debug=False, threaded=True)

    def receive_prepared_session(self):
        # get from queue a single prepared session and then validate.
        # get is set block in order to stop the application waiting for the session
        prepared_session = JsonBasedIO.get_instance()._json_queue.get(block=True)

        # validate data coming from preparation
        self.validate_json(prepared_session, 'schemas/prepared_session_schema.json')
        return prepared_session

    def post(self):
        # when a msg is received the json data is put in the queue
        json_content = request.get_json()
        JsonBasedIO.get_instance().put_json_into_queue(json_content)
        return 'OK', 201

    def receive_config_params(self, config_path, config_schema_path):
        with open(config_path, 'r') as configuration:
            json_content = json.load(configuration)
        self.validate_json(json_content, config_schema_path)
        return json_content

    # send restart used for sending at the service class the information that a test is not passed
    def send_restart_configuration(self):
        endpoint = "http://" + self._msg_sys_ip + ":" + str(self._msg_sys_port) + "/service/messaging_system"
        restart_config = {"action": "restart"}
        requests.post(endpoint, json=restart_config)

    def send_timestamp(self, timestamp, phase):  # For testing purposes
        endpoint = "http://" + self._service_class_ip + ":" + str(self._service_class_port) + "/service/log_timestamp"
        message = {'system': 'Segregation System', 'phase': phase, 'timestamp': timestamp}
        requests.post(endpoint, json=message)

    def send_learning_sets(self, learning_sets):
        endpoint = "http://" + self._dev_sys_ip + ":" + str(self._dev_sys_port) + "/DevelopmentSystem"
        requests.post(endpoint, json=learning_sets)

    def _set_global_configuration(self):
        with open("../global_configuration.json", 'r') as configuration:
            json_content = json.load(configuration)
        self.validate_json(json_content, "../global_configuration_schema.json")
        self._service_class_ip = json_content["Service Class"]["ip"]
        self._service_class_port = json_content["Service Class"]["port"]
        self._msg_sys_ip = json_content["Messaging System"]["ip"]
        self._msg_sys_port = json_content["Messaging System"]["port"]
        self._segr_sys_ip = json_content["Segregation System"]["ip"]
        self._segr_sys_port = json_content["Segregation System"]["port"]
        self._dev_sys_ip = json_content["Development System"]["ip"]
        self._dev_sys_port = json_content["Development System"]["port"]


# endpoint to communicate with this system
api.add_resource(JsonBasedIO, '/SegregationSystem')
