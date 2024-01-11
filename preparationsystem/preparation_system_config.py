import json

from preparationsystem.preparation_system_json_io import PreparationSystemJsonIO

# class to model the configuration parameters of the preparation system


class PreparationSystemConfig:
    def __init__(self, json_path):
        # Read configuration data from the specified JSON file
        with open(json_path, 'r') as file:
            json_data = json.load(file)

        # Read global configuration data from a separate global JSON file
        with open("../global_configuration.json", 'r') as f:
            global_config_data = json.load(f)

        # Get an instance of PreparationSystemJsonIO for JSON validation
        preparation_system_json_io = PreparationSystemJsonIO.get_instance()

        # Validate the JSON data against the schema for Preparation System configuration
        preparation_system_json_io.validate_json(json_data, "./schemas/preparation_system_config_schema.json")

        # Validate the global configuration data against its schema
        preparation_system_json_io.validate_json(global_config_data, "../global_configuration_schema.json")

        # Extract relevant parameters from the JSON data for Preparation System configuration
        self.development_phase = json_data.get('development_phase')
        self.max_value = json_data.get('max_value')
        self.min_value = json_data.get('min_value')
        self.service_flag = json_data.get('service_flag')

        # Extract Preparation System configuration parameters from global configuration
        self.preparation_ip = global_config_data['Preparation System']['ip']
        self.preparation_port = global_config_data['Preparation System']['port']

        # Extract Segregation System configuration parameters from global configuration
        self.segregation_ip = global_config_data['Segregation System']['ip']
        self.segregation_port = global_config_data['Segregation System']['port']

        # Extract Production System configuration parameters from global configuration
        self.production_ip = global_config_data['Production System']['ip']
        self.production_port = global_config_data['Production System']['port']

        # Extract Service Class configuration parameters from global configuration
        self.service_ip = global_config_data['Service Class']['ip']
        self.service_port = global_config_data['Service Class']['port']
