import json
import queue

import requests
from flask import request, Flask
import jsonschema
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class IngestionSystemJsonIO(Resource):
    # Singleton instance for IngestionSystemJsonIO
    instance = None

    def __init__(self):
        # Paths to JSON schemas and a queue for records
        self.__record_schema_path = "./schemas/record_schema.json"
        self.__raw_session_schema_path = "./schemas/raw_session_schema.json"
        self.__record_queue = queue.Queue()

    @staticmethod
    def get_instance():
        # Singleton pattern to ensure only one instance exists
        if IngestionSystemJsonIO.instance is None:
            IngestionSystemJsonIO.instance = IngestionSystemJsonIO()
        return IngestionSystemJsonIO.instance

    def send_raw_session(self, raw_session, preparation_ip, preparation_port) -> None:
        # Send raw session data to Preparation System
        endpoint = "http://" + preparation_ip + ":" + str(preparation_port) + "/PreparationSystem"
        raw_session_json = raw_session.to_json()
        requests.post(endpoint, json=raw_session_json)

    def send_label(self, label_json, evaluation_ip, evaluation_port) -> None:
        # Send label data to Evaluation System
        endpoint = "http://" + evaluation_ip + ":" + str(evaluation_port) + "/EvaluationSystem"
        requests.post(endpoint, json=label_json)

    def post(self):
        # Receive and process JSON data posted to ingestionsystem endpoint
        message_str = request.get_json()
        message = json.loads(message_str)
        try:
            if message['content'] == "record":
                # Validate JSON against record schema and add to the queue
                self.validate_json(message, self.__record_schema_path)
                IngestionSystemJsonIO.get_instance().__record_queue.put(message)
                return {'answer': 'ok'}, 201
            else:
                return {'answer': 'error_in_content'}, 403
        except ValueError:
            return {'answer': 'error_invalid_json'}, 403

    def validate_json(self, json_content, json_schema_path):
        # Validate JSON content against the provided JSON schema
        with open(json_schema_path, 'r') as schema:
            json_schema = json.load(schema)
        jsonschema.validate(json_content, json_schema)

    def listener(self, ip, port):
        # Start the Flask application to listen for incoming requests
        app.run(host=ip, port=port, debug=False, threaded=True)

    def recv_record(self):
        # Retrieve a record from the queue (blocking if the queue is empty)
        return IngestionSystemJsonIO.get_instance().__record_queue.get(block=True)


# Add the IngestionSystemJsonIO resource to the API at the '/ingestionsystem' endpoint
api.add_resource(IngestionSystemJsonIO, '/IngestionSystem')
