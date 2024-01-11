"""
Module: label_storage_controller.py
Author: Nicolò Salti

Classes:
    LabelStorageController: class which is used to handle the storage of labels
"""
from database.database_manager import DatabaseManager
from evaluationsystem.label import Label


class LabelStorageController:
    """
    This class is used to handle the storage of labels
    """
    def __init__(self, db_name):
        """
        Constructor of the class, it contains a reference to a DatabaseManager instance
        that is used to handle the connection with the db, execute commit queries and
        select queries
        :param
            db_name: name of the db
        """
        self.db = DatabaseManager(db_name)

    def create_label_table(self):
        """
        This method is used to create the table containing the labels
        """
        table = "label"
        query = f"DROP TABLE if exists {table};"
        self.db.commit_query(query)
        query = f"CREATE TABLE if not exists {table} (" \
                "uuid VARCHAR(255)," \
                "anomalous INT," \
                "label_type INT," \
                "PRIMARY KEY (uuid, anomalous, label_type));"

        self.db.commit_query(query)

    def store_label(self, label):
        """
        This method is used to store an object corresponding to a label in the database
        :param
            label: label to be stored
        """
        uuid = label.get_uuid()
        anomalous = label.get_anomalous()
        label_type = label.get_label_type()

        table = "label"
        query = f"INSERT INTO {table} VALUES (\"{uuid}\", {anomalous}, {label_type});"
        self.db.commit_query(query)

    def remove_label(self, labels):
        """
        This method is used to remove a list of labels from the database
        :param
            labels: list of labels to be removed
        """
        table = "label"
        for label in labels:
            uuid = label.get_uuid()
            anomalous = label.get_anomalous()
            label_type = label.get_label_type()
            query = f"DELETE FROM {table} WHERE uuid=\"{uuid}\" " \
                    f"AND anomalous={anomalous} AND label_type={label_type};"
            self.db.commit_query(query)

    # function used to get, ordered by uuid, a number of labels to generate
    # the evaluation report
    def get_stored_labels(self, num_labels):
        """
        This method is used to apply a select query to get an ordered list of labels
        :param
            num_labels: number of labels to be returned
        :return:
            classifier_labels: list of classifier labels
            expert_labels: list of expert labels
        """
        table = "label"
        query = f"SELECT * FROM {table} ORDER BY uuid LIMIT {num_labels};"
        rows = self.db.select_query(query)

        classifier_labels = []
        expert_labels = []
        for row in rows:
            if row[2] == 0:
                classifier_labels.append(Label(row[0], row[1], row[2]))
            else:
                expert_labels.append(Label(row[0], row[1], row[2]))

        return classifier_labels, expert_labels
