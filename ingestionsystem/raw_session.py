# class to model the raw session, composed by the uuid, the  three records and the label


class RawSession:
    def __init__(self, uuid=None, power_management_record=None, production_management_record=None,
                 machine_management_record=None, label=None):
        # Constructor to initialize the RawSession
        self.__uuid = uuid
        self.__power_management_record = power_management_record
        self.__production_management_record = production_management_record
        self.__machine_management_record = machine_management_record
        self.__label = label

    def get_uuid(self):
        # Getter method to retrieve the UUID of the RawSession
        return self.__uuid

    def get_power_management_record(self):
        # Getter method to retrieve the power management record of the RawSession
        return self.__power_management_record

    def get_production_management_record(self):
        # Getter method to retrieve the production management record of the RawSession
        return self.__production_management_record

    def get_machine_management_record(self):
        # Getter method to retrieve the machine management record of the RawSession
        return self.__machine_management_record

    def get_label(self):
        # Getter method to retrieve the label of the RawSession
        return self.__label

    def set_uuid(self, uuid):
        # Setter method to update the UUID of the RawSession
        self.__uuid = uuid

    def set_power_management_record(self, power_management_record):
        # Setter method to update the power management record of the RawSession
        self.__power_management_record = power_management_record

    def set_production_management_record(self, production_management_record):
        # Setter method to update the production management record of the RawSession
        self.__production_management_record = production_management_record

    def set_machine_management_record(self, machine_management_record):
        # Setter method to update the machine management record of the RawSession
        self.__machine_management_record = machine_management_record

    def set_label(self, label):
        # Setter method to update the label of the RawSession
        self.__label = label

    def to_json(self):
        # Convert RawSession data to a JSON format
        json_data = {
            "content": "raw_session",
            "uuid": self.get_uuid(),
            "power_management_record": {
                "uuid": self.get_power_management_record().get_uuid(),
                "vars": ','.join(map(str, self.get_power_management_record().get_power_vars()))
            },
            "machine_management_record": {
                "uuid": self.get_machine_management_record().get_uuid(),
                "level": self.get_machine_management_record().get_level()
            },
            "production_management_record": {
                "uuid": self.get_production_management_record().get_uuid(),
                "type": self.get_production_management_record().get_production_type()
            },
            "label": {
                "uuid": self.get_label().get_uuid(),
                "value": float(self.get_label().get_anomalous()),
                "sender": self.get_label().get_label_type()
            }
        }

        return json_data
