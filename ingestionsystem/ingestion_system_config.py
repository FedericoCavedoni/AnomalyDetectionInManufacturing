import json

from ingestionsystem.ingestion_system_json_io import IngestionSystemJsonIO


# class to model the configuration parameters of the ingestion system

class IngestionSystemConfig:
    def __init__(self, json_path: str):
        # Read the configuration data from the specified JSON file
        with open(json_path, 'r') as file:
            json_data = json.load(file)

        # Read global configuration data from a separate global JSON file
        with open("../global_configuration.json", 'r') as f:
            global_config_data = json.load(f)

        # Get an instance of IngestionSystemJsonIO for JSON validation
        ingestion_system_json_io = IngestionSystemJsonIO.get_instance()

        # Validate the JSON data against the schema for Ingestion System configuration
        ingestion_system_json_io.validate_json(json_data, "./schemas/ingestion_system_config_schema.json")

        # Validate the global configuration data against its schema
        ingestion_system_json_io.validate_json(global_config_data, "../global_configuration_schema.json")

        # Extract relevant parameters from the JSON data for Ingestion System configuration
        self.development_phase = json_data.get('development_phase')
        self.evaluation_phase_number_of_sessions = json_data.get('evaluation_phase_number_of_sessions')
        self.evaluation_phase_total_number_of_sessions = json_data.get('evaluation_phase_total_number_of_sessions')
        self.minimum_records = json_data.get('minimum_records')
        self.missing_samples_threshold = json_data.get('missing_samples_threshold')
        self.service_flag = json_data.get('service_flag')

        # Extract Ingestion System configuration parameters from global configuration
        self.ingestion_ip = global_config_data['Ingestion System']['ip']
        self.ingestion_port = global_config_data['Ingestion System']['port']

        # Extract Preparation System configuration parameters from global configuration
        self.preparation_ip = global_config_data['Preparation System']['ip']
        self.preparation_port = global_config_data['Preparation System']['port']

        # Extract Evaluation System configuration parameters from global configuration
        self.evaluation_ip = global_config_data['Evaluation System']['ip']
        self.evaluation_port = global_config_data['Evaluation System']['port']

        # Extract Service Class configuration parameters from global configuration
        self.service_ip = global_config_data['Service Class']['ip']
        self.service_port = global_config_data['Service Class']['port']
