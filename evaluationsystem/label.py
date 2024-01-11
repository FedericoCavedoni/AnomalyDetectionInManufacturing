"""
Module: label.py
Author: Nicolò Salti

Classes:
    Label: model class to represent a label
"""


class Label:
    """
    Model class to represent a label object
    """
    def __init__(self, uuid, anomalous, label_type):
        """
        Constructor of a label object
        :param
            uuid: identifier of the label
        :param
            anomalous: classification of the label (as anomalous or not)
        :param
            label_type: classifier labels (0) or expert labels (1)
        """
        self._uuid = uuid
        self._anomalous = anomalous
        self._label_type = label_type

    def get_uuid(self):
        """
        :return:
            _uuid: identifier of the label
        """
        return self._uuid

    def get_anomalous(self):
        """
        :return:
            _anomalous: classification of the label (as anomalous or not)
        """
        return self._anomalous

    def get_label_type(self):
        """
        :return:
            _label_type: classifier labels (0) or expert labels (1)
        """
        return self._label_type

    def set_uuid(self, new_uuid):
        """
        :param
            new_uuid: uuid to be set
        """
        self._uuid = new_uuid

    def set_anomalous(self, new_anomalous):
        """
        :param
            new_anomalous: classification of the label to be set
        """
        self._anomalous = new_anomalous

    def set_label_type(self, new_label_type):
        """
        :param
            new_label_type: label type to be set (expert or classifier)
        """
        self._label_type = new_label_type

    def to_dict(self):
        """
        :return:
            dictionary representation of the label
        """
        return {
            'uuid': self._uuid,
            'anomalous': self._anomalous,
            'label_type': self._label_type
        }
