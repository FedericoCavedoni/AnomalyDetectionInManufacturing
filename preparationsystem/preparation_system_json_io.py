import queue

import jsonschema
from flask_restful import Resource, Api

import json

import requests
from flask import request, Flask

app = Flask(__name__)
api = Api(app)


class PreparationSystemJsonIO(Resource):
    instance = None

    def __init__(self):
        # Initialize the paths for JSON schemas and the raw session queue
        self.__prepared_session_path = "./schemas/prepared_session_schema.json"
        self.__raw_session_schema_path = "../ingestionsystem/schemas/raw_session_schema.json"
        self.__raw_session_queue = queue.Queue()

    @staticmethod
    def get_instance():
        # Singleton pattern: Get an instance of the class, creating one if it doesn't exist
        if PreparationSystemJsonIO.instance is None:
            PreparationSystemJsonIO.instance = PreparationSystemJsonIO()

        return PreparationSystemJsonIO.instance

    def send_prepared_session(self, prepared_session, ip, port, system):
        # Send a prepared session to the specified system using HTTP POST request
        endpoint = "http://" + ip + ":" + str(port) + system
        prepared_session_json = prepared_session.to_dict()
        requests.post(endpoint, json=prepared_session_json)

    def post(self):
        # Handle incoming POST requests
        message = request.get_json()
        try:
            if message['content'] == "raw_session":
                # Validate the incoming JSON against the raw session schema
                self.validate_json(message, self.__raw_session_schema_path)

                # Put the raw session message into the queue for further processing
                PreparationSystemJsonIO.get_instance().__raw_session_queue.put(message)
                return {'answer': 'ok'}, 201
            else:
                return {'answer': 'error_in_content'}, 403
        except ValueError:
            return {'answer': 'error_invalid_json'}, 403

    def validate_json(self, json_content, json_schema_path):
        # Validate JSON content against a specified JSON schema
        with open(json_schema_path, 'r') as schema:
            json_schema = json.load(schema)
        jsonschema.validate(json_content, json_schema)

    def listener(self, ip, port):
        # Start the Flask listener for incoming requests
        app.run(host=ip, port=port, debug=False, threaded=True)

    def recv_raw_session(self):
        # Receive raw sessions from the queue
        return PreparationSystemJsonIO.get_instance().__raw_session_queue.get(block=True)


api.add_resource(PreparationSystemJsonIO, '/PreparationSystem')
