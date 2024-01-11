from service_class_io import ServiceClassIO


class ConfigurationParametersService:
    @staticmethod
    def load_configuration():  # It loads the configuration parameters into static fields of the class
        service_class_io = ServiceClassIO.get_instance()
        config_parameters = service_class_io.get_initial_configuration()
        ConfigurationParametersService.DEVELOPMENT_PHASE = config_parameters['DEVELOPMENT_PHASE']
        ConfigurationParametersService.DEVELOPMENT_SESSIONS = config_parameters['DEVELOPMENT_SESSIONS']
        ConfigurationParametersService.PRODUCTION_SESSIONS = config_parameters['PRODUCTION_SESSIONS']
        ConfigurationParametersService.EVALUATION_SESSIONS = config_parameters['EVALUATION_SESSIONS']

