import json
import random
import requests
import queue

import jsonschema

from flask import Flask, request

app = Flask(__name__)


class RandomNumberGenerator:
    def __init__(self, lower_limit, upper_limit):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.used_numbers = set()

    def generate_unique_random_number(self):
        available_numbers = set(range(self.lower_limit, self.upper_limit)) - self.used_numbers
        if not available_numbers:
            return -1
        random_number = random.choice(list(available_numbers))
        self.used_numbers.add(random_number)
        return random_number


class ServiceClassIO:
    service_instance = None

    def __init__(self):
        with open("../global_configuration.json", 'r') as global_config_params:
            global_json_content = json.load(global_config_params)
        self._validate_json(global_json_content, "../global_configuration_schema.json")
        self.service_ip = global_json_content['Service Class']['ip']
        self.service_port = global_json_content['Service Class']['port']
        self.evaluation_ip = global_json_content['Evaluation System']['ip']
        self.evaluation_port = global_json_content['Evaluation System']['port']
        self.messaging_ip = global_json_content['Messaging System']['ip']
        self.messaging_port = global_json_content['Messaging System']['port']
        self.ingestion_ip = global_json_content['Ingestion System']['ip']
        self.ingestion_port = global_json_content['Ingestion System']['port']
        self.preparation_ip = global_json_content['Preparation System']['ip']
        self.preparation_port = global_json_content['Preparation System']['port']
        self.segregation_ip = global_json_content['Segregation System']['ip']
        self.segregation_port = global_json_content['Evaluation System']['port']
        self.development_ip = global_json_content['Development System']['ip']
        self.development_port = global_json_content['Development System']['port']
        self.production_ip = global_json_content['Production System']['ip']
        self.production_port = global_json_content['Production System']['port']
        self._msg_queue = queue.Queue()
        self.rng = None

    @staticmethod
    def get_instance():
        if ServiceClassIO.service_instance is None:
            ServiceClassIO.service_instance = ServiceClassIO()

        return ServiceClassIO.service_instance

    def get_csv_file_lines(self, file_path):
        csv_lines = []
        with open(file_path, 'r') as csv_file:
            file_content = csv_file.read()
            lines = file_content.split('\n')

        for line in lines:
            if line:
                csv_lines.append(line)

        return csv_lines

    def recv_msg(self, block=True):
        return self._msg_queue.get(block=block)

    def _put_msg_into_queue(self, msg):
        self._msg_queue.put(msg)

    def send_records(self, csv_lines_power, csv_lines_production, csv_lines_machine, csv_lines_label):
        random_index = self.rng.generate_unique_random_number()
        random_line_power = csv_lines_power[random_index]
        random_line_production = csv_lines_production[random_index]
        random_line_machine = csv_lines_machine[random_index]
        random_line_label = csv_lines_label[random_index]
        values_list_power = random_line_power.split(',', 1)
        values_list_production = random_line_production.split(',')
        values_list_machine = random_line_machine.split(',')
        values_list_label = random_line_label.split(',')
        record_power = {
            "content": "record",
            "uuid": str(values_list_power[0]),
            "record_type": "power",
            "vars": values_list_power[1]
        }
        record_production = {
            "content": "record",
            "uuid": str(values_list_production[0]),
            "record_type": "production",
            "vars": values_list_production[1]
        }
        record_machine = {
            "content": "record",
            "uuid": str(values_list_machine[0]),
            "record_type": "machine",
            "vars": values_list_machine[1]
        }
        record_label = {
            "content": "record",
            "uuid": str(values_list_label[0]),
            "record_type": "label",
            "vars": values_list_label[1]
        }
        url = "http://" + self.ingestion_ip + ":" + str(self.ingestion_port) + "/IngestionSystem"
        requests.post(url, json=json.dumps(record_power))
        requests.post(url, json=json.dumps(record_machine))
        requests.post(url, json=json.dumps(record_production))
        requests.post(url, json=json.dumps(record_label))

    def get_initial_configuration(self):
        with open("configuration/service_class_configuration.json", 'r') as configuration:
            json_content = json.load(configuration)
        self._validate_json(json_content, "schemas/service_class_config_schema.json")
        return json_content

    def _validate_json(self, json_content, json_schema_path):
        with open(json_schema_path, 'r') as schema:
            json_schema = json.load(schema)
        jsonschema.validate(json_content, json_schema)


@app.route("/service/log_timestamp", methods=['POST'])
def log_timestamp():
    json_content = request.get_json()
    with open("data/log.log", "a") as f:
        f.write(str(json_content['timestamp']) + ","
                + str(json_content['system']) + "," + str(json_content['phase']) + '\n')

    return 'OK', 201


@app.route("/service/messaging_system", methods=['POST'])
def receive_messaging_system():
    json_content = request.get_json()
    if json_content['action'] == "restart" or json_content['action'] == "start production":
        ServiceClassIO.get_instance()._put_msg_into_queue(json_content)
        return 'OK', 201
    return 'ERROR', 403


@app.route("/service/client", methods=['POST'])
def receive_label():
    json_content = request.get_json()
    print(json_content)
    return 'OK', 201


def listener():
    app.run(host=ServiceClassIO.get_instance().service_ip, port=ServiceClassIO.get_instance().service_port, debug=False,
            threaded=True)
