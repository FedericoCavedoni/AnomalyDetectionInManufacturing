from development_system_io import DevelopmentSysIO


class ConfigurationParameters:
    @staticmethod
    def load_configuration():  # It loads the configuration parameters into static fields of the class
        dev_sys_io = DevelopmentSysIO.get_instance()
        config_parameters = dev_sys_io.get_initial_configuration()
        ConfigurationParameters.MIN_LAYERS: int = config_parameters["MIN_LAYERS"]
        ConfigurationParameters.MAX_LAYERS: int = config_parameters["MAX_LAYERS"]
        ConfigurationParameters.STEP_LAYERS: int = config_parameters["STEP_LAYERS"]
        ConfigurationParameters.MIN_NEURONS: int = config_parameters["MIN_NEURONS"]
        ConfigurationParameters.MAX_NEURONS: int = config_parameters["MAX_NEURONS"]
        ConfigurationParameters.STEP_NEURONS: int = config_parameters["STEP_NEURONS"]
        ConfigurationParameters.OVERFITTING_TOLERANCE: float = config_parameters["OVERFITTING_TOLERANCE"]
        ConfigurationParameters.TEST_ERROR_TOLERANCE: float = config_parameters["TEST_ERROR_TOLERANCE"]
        ConfigurationParameters.SERVICE_FLAG: bool = config_parameters["SERVICE_FLAG"]
