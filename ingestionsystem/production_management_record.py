# class to model the records arriving from the production management system

class ProductionManagementRecord:
    def __init__(self, uuid, production_type):
        # Constructor to initialize the ProductionManagementRecord with a UUID and production type
        self.__uuid = uuid
        self.__production_type = production_type

    def get_uuid(self):
        # Getter method to retrieve the UUID of the ProductionManagementRecord
        return self.__uuid

    def get_production_type(self):
        # Getter method to retrieve the production type of the ProductionManagementRecord
        return self.__production_type

    def set_uuid(self, uuid):
        # Setter method to update the UUID of the ProductionManagementRecord
        self.__uuid = uuid

    def set_production_type(self, production_type):
        # Setter method to update the production type of the ProductionManagementRecord
        self.__production_type = production_type
