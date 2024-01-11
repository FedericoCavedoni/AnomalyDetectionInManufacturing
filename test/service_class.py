import time
from threading import Thread

from service_class_io import ServiceClassIO, listener, RandomNumberGenerator
from configuration_parameters_service import ConfigurationParametersService

service_class = ServiceClassIO.get_instance()


class ServiceClass:
    def __init__(self):
        self._csv_lines_power = service_class.get_csv_file_lines("../data/powerManagementSys.csv")
        self._csv_lines_production = service_class.get_csv_file_lines("../data/productionManagementSys.csv")
        self._csv_lines_machine = service_class.get_csv_file_lines("../data/machineManagementSys.csv")
        self._csv_lines_label = service_class.get_csv_file_lines("../data/labels.csv")

    def send_records_client_sys(self):
        if ConfigurationParametersService.DEVELOPMENT_PHASE:
            n_sessions = ConfigurationParametersService.DEVELOPMENT_SESSIONS
        else:  # This case is not used (it is thought for NOT sending labels during production)
            n_sessions = (ConfigurationParametersService.PRODUCTION_SESSIONS +
                          ConfigurationParametersService.EVALUATION_SESSIONS)
        record_counter = 0
        service_class.rng = RandomNumberGenerator(1, 700)
        while record_counter < n_sessions:
            service_class.send_records(self._csv_lines_power, self._csv_lines_production,
                                       self._csv_lines_machine, self._csv_lines_label)
            record_counter += 1
        print("END RECORDS")

    def test(self):
        with open("data/log.log", "a") as f:
            f.write(str(time.time()) + ",Service Class,START\n")
        rest_server = Thread(target=listener)
        rest_server.setDaemon(True)
        rest_server.start()
        while True:
            self.send_records_client_sys()
            message = service_class.recv_msg()  # Wait for 'start production' or 'restart'
            print(message['action'])
            if message['action'] == 'start production':
                with open("data/log.log", "a") as f:
                    f.write(str(time.time()) + ",Service Class,END\n")
                time.sleep(1)
                exit(0)
            if not ConfigurationParametersService.DEVELOPMENT_PHASE and message['action'] == 'restart':
                with open("data/log.log", "a") as f:
                    f.write(str(time.time()) + ",Service Class,RESTART\n")
                time.sleep(1)
                exit(0)


if __name__ == '__main__':
    ConfigurationParametersService.load_configuration()
    ServiceClass().test()
