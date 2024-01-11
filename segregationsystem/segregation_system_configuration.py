import json


class ConfigurationParameters:

    def __init__(self):
        with open('configuration/segregation_configuration.json', 'r') as file:
            json_data = json.load(file)

        self.tolerance_interval = json_data.get('toleranceInterval')
        self.session_number = json_data.get('sessionNumber')

        self.training_set_size = json_data.get('training_set_size')
        self.testing_set_size = json_data.get('testing_set_size')
        self.validation_set_size = json_data.get('validation_set_size')

        self.service_flag = json_data.get('service_flag')

    def get_tolerance_interval(self):
        return self.tolerance_interval

    def get_session_number(self):
        return self.session_number

    def get_training_set_size(self):
        return self.training_set_size

    def get_testing_set_size(self):
        return self.testing_set_size

    def get_validation_set_size(self):
        return self.validation_set_size

    def get_service_flag(self):
        return self.service_flag
