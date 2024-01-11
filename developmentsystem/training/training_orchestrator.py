import random
import json
import math
from time import sleep

import joblib

from developmentsystem.training.learning_error import LearningError
from developmentsystem.training.learning_report_view import LearningReportView
from developmentsystem.training.classifier_trainer import ClassifierTrainer
from developmentsystem.configuration_parameters import ConfigurationParameters


class TrainingOrchestrator:
    def __init__(self):
        self._service_flag: bool = ConfigurationParameters.SERVICE_FLAG

    # 'step' argument can be "start", "set_#iterations", "check_learning_plot"
    def train_classifier(self, step: str, human_task_json: dict = None):
        if step == "start":
            classifier_trainer = ClassifierTrainer()
            print("SET AVERAGE HYPERPARAMETERS")
            classifier_trainer.set_average_hyperparameters()
            if self._service_flag:  # Stop&Go is simplified, the human choice is statistically generated
                while True:
                    current_iterations = self._set_iterations_and_train(random.randint(50, 150), classifier_trainer)
                    generated_choice = random.randint(0, 4)
                    if generated_choice == 0:  # 20%
                        print("CHECK LEARNING PLOT (STATISTICALLY GENERATED: ok)")
                        return current_iterations
                    if generated_choice <= 2:  # 40%
                        print("CHECK LEARNING PLOT (STATISTICALLY GENERATED: increase by one third)")
                        new_iterations = math.ceil(current_iterations * (1 + 1 / 3))
                        self._set_iterations_and_train(new_iterations, classifier_trainer)
                    else:  # 40%
                        print("CHECK LEARNING PLOT (STATISTICALLY GENERATED: reduce by one third)")
                        new_iterations = math.ceil(current_iterations * (1 - 1 / 3))
                        self._set_iterations_and_train(new_iterations, classifier_trainer)
            else:
                set_iterations_json = {'human_task': 'set_#iterations', 'human_choice': 0}
                with open('data/stop&go.json', 'w') as f:
                    json.dump(set_iterations_json, f)
                joblib.dump(classifier_trainer, "data/classifier_trainer")
                sleep(1)  # For testing
                return -1
        elif step == "set_#iterations":
            self._set_iterations_and_train(human_task_json["human_choice"])
            print("CHECK LEARNING PLOT (HUMAN TASK)")
            return -1
        if step == "check_learning_plot":
            human_choice = human_task_json['human_choice']
            current_iterations = human_task_json['current_iterations']
            if human_choice == "ok":
                return current_iterations
            if human_choice == "increase_one_third":
                new_iterations = math.ceil(current_iterations * (1 + 1 / 3))
                self._set_iterations_and_train(new_iterations)
            else:  # "reduce_one_third"
                new_iterations = math.ceil(current_iterations * (1 - 1 / 3))
                self._set_iterations_and_train(new_iterations)
            print("CHECK LEARNING PLOT (HUMAN TASK)")
            return -1

    def _set_iterations_and_train(self, num_iterations: int, classifier_trainer: ClassifierTrainer = None):
        if classifier_trainer is None and not self._service_flag:
            classifier_trainer = joblib.load("data/classifier_trainer")
        print("SET # ITERATIONS")
        classifier_trainer.set_num_iterations(num_iterations)
        print("TRAIN")
        classifier = classifier_trainer.train()
        print("GENERATE LEARNING REPORT")
        learning_report = LearningError(classifier.get_loss_curve())
        LearningReportView().generate_learning_report(learning_report)
        if not self._service_flag:
            check_learning_plot = {'human_task': 'check_learning_plot',
                                   'current_iterations': len(learning_report.get_learning_error()),
                                   'human_choice': 'ok/increase_one_third/reduce_one_third'
                                   }
            with open('data/stop&go.json', 'w') as f:
                json.dump(check_learning_plot, f)
        return num_iterations
