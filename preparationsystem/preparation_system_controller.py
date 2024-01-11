import json
import time
from threading import Thread

from flask import Flask
from flask_restful import Api


from preparationsystem.preparation_system_json_io import PreparationSystemJsonIO
from evaluationsystem.label import Label
from ingestionsystem.machine_management_record import MachineManagementRecord
from ingestionsystem.power_management_record import PowerManagementRecord
from ingestionsystem.production_management_record import ProductionManagementRecord
from ingestionsystem.raw_session import RawSession
from preparationsystem.features_extractor import FeaturesExtractor
from preparationsystem.preparation_system_config import PreparationSystemConfig
from preparationsystem.session_correction import SessionCorrection
from utilities.utils import Utils

app = Flask(__name__)
api = Api(app)


class PreparationSystemController:
    def __init__(self):
        # Initialize preparation system configuration and get the JSON I/O instance
        self.__preparation_system_config = PreparationSystemConfig("./config/preparation_system_config.json")
        self.__preparation_system_json_io = PreparationSystemJsonIO.get_instance()

    def get_preparation_system_config(self):
        return self.__preparation_system_config

    def set_preparation_system_config(self, preparation_system_config):
        self.__preparation_system_config = preparation_system_config

    def run(self):
        print("STARTED")
        # Start a listener thread for receiving raw sessions
        listener = Thread(target=self.__preparation_system_json_io.listener,
                          args=(self.__preparation_system_config.preparation_ip,
                                self.__preparation_system_config.preparation_port))
        listener.setDaemon(True)
        listener.start()

        # variable to maintain the last received values of the records, it is used to correct missing samples
        # initially default values are used
        # 0: production, 1: machine
        lasts_static_records_values = ['facial', 'heavy']  # DEFAULT

        while True:
            # hangs waiting to receive a raw session
            raw_session_json = self.__preparation_system_json_io.recv_raw_session()
            print("RAW SESSION RECEIVED")

            # send start timestamp to the service class
            if self.__preparation_system_config.service_flag:
                Utils.send_timestamp("Preparation System", self.__preparation_system_config.service_ip,
                                     self.__preparation_system_config.service_port, time.time(), "start")

            # construction of a RawSession object starting from the received json
            raw_session = self.generate_raw_session_from_json(raw_session_json)

            # CORRECT MISSING SAMPLES
            # Correct missing samples in the time series and static records
            session_correction = SessionCorrection()
            power_vars = raw_session.get_power_management_record().get_power_vars()
            session_correction.correct_missing_samples_time_series(power_vars)
            session_correction.correct_missing_samples_static_records([raw_session.get_production_management_record(),
                                                                       raw_session.get_machine_management_record()],
                                                                      lasts_static_records_values)

            # DETECT AND CORRECT ABSOLUTE OUTLIERS
            # Detect and correct absolute outliers in the power time series
            session_correction.detect_and_correct_absolute_outliers(power_vars,
                                                                    self.__preparation_system_config.max_value,
                                                                    self.__preparation_system_config.min_value)
            raw_session.get_power_management_record().set_power_vars(power_vars)

            # EXTRACT FEATURES
            # Extract features from the raw session
            features_extractor = FeaturesExtractor()
            prepared_session = features_extractor.extract_features(raw_session)

            # IF DEVELOPMENT PHASE
            # If it's the development phase, send the prepared session to the segregation system,
            # otherwise send it to the production system
            if self.__preparation_system_config.development_phase:
                # send prepared session to segregation system
                self.__preparation_system_json_io.send_prepared_session(prepared_session,
                                                                        self.__preparation_system_config.segregation_ip,
                                                                        self.__preparation_system_config.segregation_port,
                                                                        "/SegregationSystem")
                print("PREPARED SESSION SENT TO SEGREGATION SYSTEM")
            else:
                # send prepared session to production system
                self.__preparation_system_json_io.send_prepared_session(prepared_session,
                                                                        self.__preparation_system_config.production_ip,
                                                                        self.__preparation_system_config.production_port,
                                                                        "/ProductionSystem")
                print("PREPARED SESSION SENT TO PRODUCTION SYSTEM")

            # send end timestamp to the service class
            if self.__preparation_system_config.service_flag:
                Utils.send_timestamp("Preparation System", self.__preparation_system_config.service_ip,
                               self.__preparation_system_config.service_port, time.time(), "end")

    def generate_raw_session_from_json(self, json_records: dict):
        # Generate a RawSession object from the received JSON
        power_vars = [float(num) for num in json_records['power_management_record']['vars'].split(",")]
        power = PowerManagementRecord(json_records['power_management_record']['uuid'], power_vars)
        production = ProductionManagementRecord(json_records['production_management_record']['uuid'],
                                                json_records['production_management_record']['type'])
        machine = MachineManagementRecord(json_records['machine_management_record']['uuid'],
                                          json_records['machine_management_record']['level'])
        label = Label(json_records['label']['uuid'],
                      json_records['label']['value'], 1)
        raw_session = RawSession(json_records['uuid'], power, production, machine, label)
        return raw_session


if __name__ == '__main__':
    preparation_controller = PreparationSystemController()
    preparation_controller.run()
