# class to model the records arriving from the machine management system

class MachineManagementRecord:
    def __init__(self, uuid, level):
        # Constructor to initialize the MachineManagementRecord with a UUID and level
        self.__uuid = uuid
        self.__level = level

    def get_uuid(self):
        # Getter method to retrieve the UUID of the MachineManagementRecord
        return self.__uuid

    def get_level(self):
        # Getter method to retrieve the level of the MachineManagementRecord
        return self.__level

    def set_uuid(self, uuid):
        # Setter method to update the UUID of the MachineManagementRecord
        self.__uuid = uuid

    def set_level(self, level):
        # Setter method to update the level of the MachineManagementRecord
        self.__level = level
