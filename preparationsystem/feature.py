# class to model a generic feature

class Feature:
    def __init__(self, name, value):
        # Constructor to initialize the Feature with a name and value
        self.__name = name
        self.__value = value

    def get_name(self):
        # Getter method to retrieve the name of the Feature
        return self.__name

    def get_value(self):
        # Getter method to retrieve the value of the Feature
        return self.__value

    def set_name(self, name):
        # Setter method to update the name of the Feature
        self.__name = name

    def set_value(self, value):
        # Setter method to update the value of the Feature
        self.__value = value
