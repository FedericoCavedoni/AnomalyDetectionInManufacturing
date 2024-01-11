from typing import TypeVar


from ingestionsystem.machine_management_record import MachineManagementRecord
from ingestionsystem.power_management_record import PowerManagementRecord
from ingestionsystem.production_management_record import ProductionManagementRecord
from ingestionsystem.raw_session import RawSession
from database.database_manager import DatabaseManager
from evaluationsystem.label import Label

T = TypeVar('T')

"""
DB SCHEMA 
TABLE Record
uuid, recordType, vars -----> record type: [power, machine, production, label]
primary key: uuid, recordType
"""


class RecordStorage:
    def __init__(self):
        # Initialize the RecordStorage with a DatabaseManager for managing records in the database passed as argument
        self.__db = DatabaseManager("sse.db")

    def get_record(self, record_type, uuid) -> T:
        # Retrieve a record from the database based on record type and uuid
        query = "SELECT * FROM record WHERE uuid = "+str(uuid)+" AND recordType = '"+record_type+"';"
        record_db = self.__db.select_query(query)
        if record_db[0][1] == "power":
            record_vars = [num for num in record_db[0][2].split(",")]
            record = PowerManagementRecord(record_db[0][0], record_vars)
            return record
        elif record_db[0][1] == "machine":
            record = MachineManagementRecord(record_db[0][0], record_db[0][2])
            return record
        elif record_db[0][1] == "production":
            record = ProductionManagementRecord(record_db[0][0], record_db[0][2])
            return record
        elif record_db[0][1] == "label":
            label = Label(record_db[0][0], record_db[0][2])
            return label

    def save_record(self, record_uuid, record_type, record_vars):
        # store a record in the db
        query = "INSERT INTO record VALUES ('" + str(record_uuid) + "','" + record_type + "','" + record_vars + "');"
        self.__db.commit_query(query)

    def remove_records(self, uuid=None):
        # remove all the records with the uuid specified from the db
        # if uuid is not specified remove everything from the db
        if uuid is None:
            query = "DELETE FROM record;"
        else:
            query = "DELETE FROM record WHERE uuid = '" + str(uuid)+"';"
        self.__db.commit_query(query)

    def get_raw_session(self, uuid):
        # Get all the records with the uuid specified
        # These records are used to build the raw session
        query = "SELECT * FROM record WHERE uuid = '" + str(uuid) + "';"
        records = self.__db.select_query(query)
        raw_session = RawSession()
        raw_session.set_uuid(uuid)
        for record in records:
            if record[1] == "power":
                record_vars = [num for num in record[2].split(",")]
                power = PowerManagementRecord(record[0], record_vars)
                raw_session.set_power_management_record(power)
            elif record[1] == "machine":
                machine = MachineManagementRecord(record[0], record[2])
                raw_session.set_machine_management_record(machine)
            elif record[1] == "production":
                production = ProductionManagementRecord(record[0], record[2])
                raw_session.set_production_management_record(production)
            elif record[1] == "label":
                label = Label(record[0], record[2], 1)
                raw_session.set_label(label)

        return raw_session
