import matplotlib.pyplot as plt

from developmentsystem.training.learning_error import LearningError


class LearningReportView:
    # Generate a plot with the #iterations on the x-axis and the training error for each iteration on the y-axis
    # It takes as input an object of type LearningError, which stores the training error for each iteration
    def generate_learning_report(self, learning_error: LearningError):
        error_curve = learning_error.get_learning_error()
        plt.plot(range(1, len(error_curve) + 1), error_curve, label="Training error")
        plt.xlabel('# iterations')
        plt.ylabel('Training error')
        plt.savefig("data/learning_plot.png")
