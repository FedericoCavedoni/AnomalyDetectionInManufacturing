# pylint: disable=import-error

"""
Module: classifier_controller.py

This module contains the implementation of the ClassifierController class.

Classes:
- ClassifierController: Controller class to manage the classifier.
"""

import joblib

from preparationsystem.prepared_session import PreparedSession
from developmentsystem.training.classifier import Classifier
from evaluationsystem.label import Label


class ClassifierController:
    """
    Controller class to manage the classifier.

    Attributes:
    - _classifier (Classifier): The classifier object used for classification.
    """

    def __init__(self):
        self._classifier: Classifier or None = None

    def classify(self, prepared_session: PreparedSession):
        """
        Classify the provided PreparedSession using the loaded classifier.

        Parameters:
        - prepared_session (PreparedSession): The PreparedSession to be classified.

        Returns:
        - Label: A Label object containing the predicted label for the provided session.
        """
        if self._classifier is None:
            self._classifier = joblib.load("model/classifier.sav")

        label_value = self._classifier.predict(prepared_session.get_features())
        label = Label(uuid=prepared_session.get_uuid(), anomalous=label_value[0], label_type=1)
        return label

    @staticmethod
    def deploy(classifier):
        """
        Deploy the provided classifier.
        This function saves the classifier to the file 'classifier.sav' in the 'model' directory.

        Parameters:
        - classifier: The classifier object to be saved.
        """
        with open("model/classifier.sav", "wb") as f:
            f.write(classifier)
