import json
import random
import matplotlib.pyplot as plt

from segregationsystem.json_based_io import JsonBasedIO
from segregationsystem.session_storage import SessionStorage


class BalancingReportPlotView:
    def __init__(self, tolerance_interval):
        self._tolerance_interval = tolerance_interval

    def generate_balancing_report_plot(self):
        storage = SessionStorage()
        prepared_sessions = storage.load_prepared_session()

        labels = ['anomalous', 'non-anomalous']
        values = [0, 0]

        # prepare data to build the bar chart
        for prepared_session in prepared_sessions:
            values[int(prepared_session[7])] += 1

        bars = plt.bar(labels, values, width=0.4, align='center')
        plt.xlabel('Features')
        plt.ylabel('Number of occurrences')
        plt.title(f'Balancing Report')
        heights = [bar.get_height() for bar in bars]

        plt.text(0.5, 1.12, f'TOLERANCE INTERVAL = {self._tolerance_interval}%',
                 horizontalalignment='center', verticalalignment='center',
                 transform=plt.gca().transAxes, bbox=dict(facecolor='white', edgecolor='black'))

        diff = abs(values[0] - values[1]) / max(values) * 100
        plt.text(0.5, 0.9, f'Difference: {diff}%', horizontalalignment='center', verticalalignment='center',
                 transform=plt.gca().transAxes, bbox=dict(facecolor='white', edgecolor='black'))

        for height in enumerate(heights):
            plt.axhline(y=height[1], linestyle='--', color='red', linewidth=1)

        # save bar chart in a png image
        try:
            plt.savefig('data/img/balancing_report.png')
            plt.close()
        except ValueError:
            return None

    # generate random number to simulate human behaviour
    # return 0 if response is ok, 1 if response is no, 2 otherwise
    def simulated_balancing_report(self):
        # simulate human behaviour with random: 20% pass 80% fail
        if random.randint(1, 5) != 1:
            data = {'evaluation': 'no'}
            print("simulazione balancing valutata no")
            return_value = 1
        else:
            data = {'evaluation': 'ok'}
            return_value = 0
        try:
            # write in json file same as it was the human
            with open('data/balancing_report.json', "w") as file:
                json.dump(data, file, indent=4)
        except ValueError:
            return 2
        return return_value

    # check json file with human decision
    # return 0 if response is ok, 1 if response is no, 2 otherwise
    def check_human_decision(self):
        # open json file with human response
        try:
            with open('data/balancing_report.json') as file:
                report = json.load(file)

            # validate response
            jsonIO = JsonBasedIO()
            jsonIO.validate_json(report, 'schemas/balancing_report_schema.json')

        except FileNotFoundError:
            return -1

        evaluation = report['evaluation']

        # for each possible response return a different code handle by the controller
        if evaluation == 'ok':
            return 0
        elif evaluation == 'no':
            return 1
        else:
            return 2
