# class to model the records arriving from the power management system

class PowerManagementRecord:
    def __init__(self, uuid, power_vars):
        # Constructor to initialize the PowerManagementRecord with a UUID and power variables
        self.__uuid = uuid
        self.__power_vars = power_vars

    def get_uuid(self):
        # Getter method to retrieve the UUID of the PowerManagementRecord
        return self.__uuid

    def get_power_vars(self):
        # Getter method to retrieve the power variables of the PowerManagementRecord
        return self.__power_vars

    def set_uuid(self, uuid):
        # Setter method to update the UUID of the PowerManagementRecord
        self.__uuid = uuid

    def set_power_vars(self, power_vars):
        # Setter method to update the power variables of the PowerManagementRecord
        self.__power_vars = power_vars
