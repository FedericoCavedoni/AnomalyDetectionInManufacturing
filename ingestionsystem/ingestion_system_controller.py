import time
from threading import Thread

from ingestionsystem.ingestion_system_config import IngestionSystemConfig
from ingestionsystem.ingestion_system_json_io import IngestionSystemJsonIO
from ingestionsystem.missing_samples import MissingSamples
from ingestionsystem.record_storage import RecordStorage

from utilities.utils import Utils


class IngestionSystemController:
    def __init__(self):
        # Initialize the IngestionSystemController with configuration and record storage
        self.__ingestion_system_config = IngestionSystemConfig("./config/ingestion_system_config.json")
        self.__record_storage = RecordStorage()
        # Initial database cleanup
        self.__record_storage.remove_records()
        # Parameters to manage the logic in the arrival of records relating to a session
        self.__last_uuid = None
        self.__record_arrived = 0
        # Get the instance of the IngestionSystemJsonIO
        self.__ingestion_system_json_io = IngestionSystemJsonIO.get_instance()

    def get_ingestion_system_config(self):
        # Getter method for the Ingestion System configuration
        return self.__ingestion_system_config

    def get_record_storage(self):
        # Getter method for the record storage
        return self.__record_storage

    def set_ingestion_system_config(self, ingestion_system_config):
        # Setter method for the Ingestion System configuration
        self.__ingestion_system_config = ingestion_system_config

    def set_record_storage(self, record_storage):
        # Setter method for the record storage
        self.__record_storage = record_storage

    def run(self) -> None:
        # Run method to start the Ingestion System Controller
        print("STARTED")

        # Start of the Flask Server thread
        listener = Thread(target=self.__ingestion_system_json_io.listener, args=(
            self.__ingestion_system_config.ingestion_ip,
            self.__ingestion_system_config.ingestion_port))
        listener.setDaemon(True)
        listener.start()

        # variables to manage the logic to decide when you are in the evaluation phase
        session_sent = 0
        session_evaluated = 0
        evaluation_phase = False

        # variables to manage the logic of the missing records
        # 0: production, 1: machine, 2: power
        records_arrived = [False, False, False]
        uuid_missing = None

        while True:
            # waiting for receiving a record
            json_record = self.__ingestion_system_json_io.recv_record()
            print("RECORD RECEIVED")

            if self.__ingestion_system_config.service_flag:
                Utils.send_timestamp("Ingestion System", self.__ingestion_system_config.service_ip,
                                     self.__ingestion_system_config.service_port, time.time(), "start")

            uuid = json_record['uuid']

            if self.__last_uuid is None:
                self.__last_uuid = uuid

            if self.__last_uuid is not None and uuid != self.__last_uuid:
                uuid_before = self.__last_uuid
                self.__last_uuid = uuid
                if self.__record_arrived < self.__ingestion_system_config.minimum_records:
                    uuid_missing = uuid_before
                    if not records_arrived[0]:
                        self.__record_storage.save_record(uuid_missing, "production", "")
                    if not records_arrived[1]:
                        self.__record_storage.save_record(uuid_missing, "machine", "")
                    if not records_arrived[2]:
                        n = 1599
                        power_vars = ',' * n
                        self.__record_storage.save_record(uuid_missing, "power", power_vars)
                else:
                    self.__record_arrived = 0
                    uuid_missing = None

            # STORE RECORD
            self.__record_storage.save_record(uuid, json_record['record_type'], json_record['vars'])
            self.__record_arrived += 1
            print("RECORD STORED")

            if json_record['record_type'] == "production":
                records_arrived[0] = True
            elif json_record['record_type'] == "machine":
                records_arrived[1] = True
            elif json_record['record_type'] == "power":
                records_arrived[2] = True

            # IF INSUFFICIENT RECORD
            if self.__record_arrived < self.__ingestion_system_config.minimum_records and uuid_missing is None:
                if self.__ingestion_system_config.service_flag:
                    Utils.send_timestamp("Ingestion System", self.__ingestion_system_config.service_ip,
                                         self.__ingestion_system_config.service_port, time.time(), "end")
                continue

            # CREATE RAW SESSION
            uuid_raw_session = uuid
            if uuid_missing is not None:
                uuid_raw_session = uuid_missing
            raw_session = self.__record_storage.get_raw_session(uuid_raw_session)
            print("RAW SESSION CREATED")

            # REMOVE RECORDS
            self.__record_storage.remove_records(raw_session.get_uuid())

            if uuid_missing is None:
                records_arrived = [False, False, False]
            else:
                uuid_missing = None

            if raw_session.get_label() is None or raw_session.get_machine_management_record() is None or \
                    raw_session.get_production_management_record() is None or \
                    raw_session.get_power_management_record() is None:
                continue

            # MARK MISSING SAMPLES
            missing_samples = MissingSamples()
            missing_samples.mark_missing_samples(raw_session.get_power_management_record().get_power_vars(),
                                                 records_arrived[:2])

            # IF RAW SESSION INVALID
            if missing_samples.get_number_of_missing_samples() > self.__ingestion_system_config.missing_samples_threshold:
                # send start timestamp to the service class
                if self.__ingestion_system_config.service_flag:
                    Utils.send_timestamp("Ingestion System", self.__ingestion_system_config.service_ip,
                                         self.__ingestion_system_config.service_port, time.time(), "end")
                continue

            # IF EVALUATION PHASE
            if evaluation_phase:
                label = raw_session.get_label()
                label_to_send = {
                    "uuid": label.get_uuid(),
                    "anomalous": float(label.get_anomalous()),
                    "sender": "expert"
                }
                self.__ingestion_system_json_io.send_label(label_to_send, self.__ingestion_system_config.evaluation_ip,
                                                           self.__ingestion_system_config.evaluation_port)
                print("LABEL SENT TO EVALUATION SYSTEM")

            # SEND RAW SESSION
            self.__ingestion_system_json_io.send_raw_session(raw_session,
                                                             self.__ingestion_system_config.preparation_ip,
                                                             self.__ingestion_system_config.preparation_port)
            print("RAW SESSION SENT TO PREPARATION SYSTEM")

            # Evaluation phase logic
            if not self.__ingestion_system_config.development_phase and evaluation_phase:
                session_evaluated += 1
                if session_evaluated == self.__ingestion_system_config.evaluation_phase_number_of_sessions:
                    session_evaluated = 0
                    evaluation_phase = False
            elif not self.__ingestion_system_config.development_phase and not evaluation_phase:
                session_sent += 1
                if session_sent == self.__ingestion_system_config.evaluation_phase_total_number_of_sessions:
                    session_evaluated = 0
                    session_sent = 0
                    evaluation_phase = True

            # send end timestamp to the service class
            if self.__ingestion_system_config.service_flag:
                Utils.send_timestamp("Ingestion System", self.__ingestion_system_config.service_ip,
                                     self.__ingestion_system_config.service_port, time.time(), "end")


if __name__ == '__main__':
    ingestion_controller = IngestionSystemController()
    ingestion_controller.run()
