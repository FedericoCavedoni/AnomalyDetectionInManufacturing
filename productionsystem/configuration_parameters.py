# pylint: disable=too-few-public-methods
# pylint: disable=import-error
# pylint: disable=line-too-long

"""
Module: configuration_parameters.py

This module contains the ConfigurationParameters class, which is responsible for managing
and retrieving configuration parameters from the production system.

Classes:
- ConfigurationParameters: Class for Configuration Parameters.
"""

from productionsystem.production_system_io import ProductionSystemIO


class ConfigurationParameters:
    """
    Class to manage Configuration Parameters.

    This class is responsible for managing and retrieving configuration parameters
    from the production system.

    Attributes:
    - service_flag (bool): Flag indicating the service status.
    - label_to_both_systems (int): Label to be sent to both systems.
    - label_only_to_client (int): Label to be sent only to the client.
    """

    def __init__(self):
        pass

    service_flag = None
    label_to_both_systems = None
    label_only_to_client = None

    @staticmethod
    def get_config_param():
        """
        Get Configuration Parameters from the configuration file.

        Returns:
        dict: Configuration parameters retrieved from the file 'configParams.json'.
        """
        prod_sys_io = ProductionSystemIO.get_instance()
        config = prod_sys_io.get_initial_configuration()

        ConfigurationParameters.service_flag = config['service_flag']
        ConfigurationParameters.label_to_both_systems = config[
            'label_to_both_systems']
        ConfigurationParameters.label_only_to_client = config[
            'label_only_to_client']
