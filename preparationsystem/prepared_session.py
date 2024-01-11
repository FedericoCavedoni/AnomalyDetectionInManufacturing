# class to model the prepared session, composed by the uuid, the list of features and the label

class PreparedSession:
    def __init__(self, uuid, features, label):
        # Constructor to initialize the PreparedSession with a UUID, features, and a label
        self.__uuid = uuid
        self.__features = features
        self.__label = label

    def get_uuid(self):
        # Getter method to retrieve the UUID of the PreparedSession
        return self.__uuid

    def get_features(self):
        # Getter method to retrieve the list of features of the PreparedSession
        return self.__features

    def get_label(self):
        # Getter method to retrieve the label of the PreparedSession
        return self.__label

    def set_uuid(self, uuid):
        # Setter method to update the UUID of the PreparedSession
        self.__uuid = uuid

    def set_features(self, features):
        # Setter method to update the list of features of the PreparedSession
        self.__features = features

    def set_label(self, label):
        # Setter method to update the label of the PreparedSession
        self.__label = label

    def to_dict(self):
        # Convert PreparedSession data to a JSON format
        return {
            'content': "prepared_session",
            'uuid': self.__uuid,
            **{f.get_name(): f.get_value() for f in self.__features},
            'label': int(self.__label.get_anomalous())
        }
