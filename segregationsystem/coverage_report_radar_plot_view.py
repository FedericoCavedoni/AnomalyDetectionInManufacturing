import json
import random

import plotly.graph_objects as go
import pandas as pd

from segregationsystem.json_based_io import JsonBasedIO


class CoverageReportRadarPlotView:
    def __init__(self, session_number):
        self._session_number = session_number

    def generate_coverage_plot(self, dataset):
        numeric_columns = dataset.columns[1:-1]
        numeric_values_dataset = dataset[numeric_columns].values
        labels = ['maximum_powerconsumptiontimeseries', 'median_powerconsumptiontimeseries',
                  'skeweness_powerconsumptiontimeseries', 'meanabsolutedeviation_powerconsumptiontimeseries',
                  'tissue_product', 'load_and_speed_type']

        pandas_dataset = pd.DataFrame(data=numeric_values_dataset, columns=labels)

        fig = go.Figure()

        for i in range(self._session_number):
            fig.add_trace(
                go.Scatterpolar(
                    r=pandas_dataset.loc[i].values.tolist(),
                    theta=pandas_dataset.columns.tolist(),
                    fill=None,
                    mode="markers"
                )
            )

        fig.update_layout(
            polar=dict(
                # axis layout definition
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            # set no legend and plot title
            showlegend=False,
            title="Coverage Report",
        )

        fig.write_image("data/img/radar_plot.png")

    # generate random number to simulate human behaviour
    # return 0 if response is ok, 1 if response is no, 2 otherwise
    def simulated_coverage_report(self):
        # simulate human behaviour with random: 33% pass 66% fail
        if random.randint(1, 3) != 1:
            data = {'evaluation': 'no'}
            print("simulazione radar valutata no")
            return_value = 1
        else:
            data = {'evaluation': 'ok'}
            return_value = 0
        try:
            # write in json file same as it was the human
            with open('data/coverage_report.json', "w") as file:
                json.dump(data, file, indent=4)
        except ValueError:
            return 2
        return return_value

    # check json file with human decision
    # return 0 if response is ok, 1 if response is no, 2 otherwise
    def check_human_decision(self):
        # open json file with human response
        try:
            with open('data/coverage_report.json') as file:
                report = json.load(file)

            # validate response
            jsonIO = JsonBasedIO()
            jsonIO.validate_json(report, 'schemas/coverage_report_schema.json')

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
