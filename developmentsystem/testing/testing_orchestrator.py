import json
import os
import random
import joblib

from pandas import read_csv
from sklearn.metrics import log_loss
from utilities.utils import Utils
from developmentsystem.testing.test_report_generator import TestReportGenerator
from developmentsystem.configuration_parameters import ConfigurationParameters
from developmentsystem.training.classifier import Classifier


class TestingOrchestrator:
    def __init__(self, classifier_index: int):
        self._winner_network: Classifier = joblib.load("data/classifier" + str(classifier_index) + ".sav")
        Utils.delete_files_pattern("data/classifier*.sav")
        self._service_flag: bool = ConfigurationParameters.SERVICE_FLAG
        self._test_report = None

    def test_classifier(self):  # Testing of the valid classifier ang generation of the test report
        self._test()
        print("GENERATE TEST REPORT")
        self._test_report = TestReportGenerator().generate_test_report(self._winner_network)
        # Save model of classifier
        joblib.dump(self._winner_network, "data/classifier.sav")
        check_test_results = {'human_task': 'check_test_results',
                              'test_report': self._test_report,
                              'human_choice': '0/1(string)'
                              }
        with open('data/stop&go.json', 'w') as f:
            json.dump(check_test_results, f)
        if not self._service_flag:
            print("CHECK TEST RESULTS (HUMAN TASK)")
            return -1
        try:
            os.remove('data/test_report.json')
        except OSError:
            pass
        os.rename('data/stop&go.json', 'data/test_report.json')
        index = int(random.random() <= 0.99)
        if index == 1:
            result = "PASSED"
        else:
            result = "NOT PASSED"
        print("CHECK TEST RESULTS (STATISTICALLY GENERATED: " + result + ")")
        return index

    def _test(self):  # Prediction of test set and computation of test error
        test_data = read_csv('data/test_set.csv')
        test_labels = test_data['label']
        del test_data['label']
        true_labels = []
        for label in test_labels:
            if label == 1.0:
                true_labels.append([1.0, 0])
            else:
                true_labels.append([0, 1.0])
        self._winner_network.set_test_error(log_loss(true_labels, self._winner_network.predict_proba(test_data)))
