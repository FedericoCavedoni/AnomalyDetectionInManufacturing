import json
import os
import time

from segregationsystem.prepared_session_manager import PreparedSessionManager
from segregationsystem.segregation_system_configuration import ConfigurationParameters
from segregationsystem.json_based_io import JsonBasedIO
from segregationsystem.coverage_report_radar_plot_view import CoverageReportRadarPlotView
from segregationsystem.balancing_report_plot_view import BalancingReportPlotView
from segregationsystem.learning_set_splitter import LearningSetSplitter
from segregationsystem.session_storage import SessionStorage

from threading import Thread


class SegregationSystemController:
    def __init__(self):
        self._parameters = ConfigurationParameters()

    def run(self):
        # start flask server with listener function to get and store
        # into a queue the prepared session received
        jsonIO = JsonBasedIO.get_instance()
        listener = Thread(target=jsonIO.listener)
        listener.setDaemon(True)
        listener.start()

        session_storage = SessionStorage()
        service_flag = self._parameters.get_service_flag()

        while True:
            stop_and_go = None
            # if stop and go is active read the stop&go file
            # then go in the correct code section
            # possible outcome null content, check_balancing_report, check_coverage_report
            if service_flag is False:
                try:
                    if os.path.getsize('data/stop&go.json') > 0:
                        with open('data/stop&go.json', 'r') as json_file:
                            stop_and_go = json.load(json_file)
                            print("READ FILE STOP&GO")
                except Exception as e:
                    print(f"Error loading json file: {str(e)}")

            # if testing mode is on or stop&go file is empty
            # start the collection of prepared sessions
            if service_flag is True or stop_and_go is None:
                session_storage.delete_prepared_sessions()
                while True:
                    # get prepared session from flask server's queue
                    prepared_session = jsonIO.receive_prepared_session()
                    jsonIO.send_timestamp(time.time(), "start")

                    # store the received session in db
                    session_storage.store_prepared_session(prepared_session)

                    prepared_session = PreparedSessionManager(self._parameters.get_session_number())

                    # check if the total number of session collected are == to the
                    # parameter insert into the system configuration, if so exit form the loop
                    if prepared_session.check_sufficient_session() is True:
                        print("SUFFICIENT PREPARED SESSIONS")
                        jsonIO.send_timestamp(time.time(), "end")
                        break

                # generate balancing report_plot
                balancingPlot = BalancingReportPlotView(self._parameters.get_tolerance_interval())
                balancingPlot.generate_balancing_report_plot()
                print("BALANCING REPORT GENERATED")

                # if stop&go is active the program will stop waiting for the user response
                if service_flag is False:
                    break

            if service_flag is True or stop_and_go['human_task'] == "check_balancing_report":

                balancingPlot = BalancingReportPlotView(self._parameters.get_tolerance_interval())

                # if testing mode is on, start the simulation to check if classes are balanced
                if service_flag is True:
                    print("HUMAN SIMULATION: EVALUATE BALANCING REPORT")
                    result = balancingPlot.simulated_balancing_report()
                # else read from file the human response
                else:
                    print("HUMAN TASK: EVALUATE BALANCING REPORT")
                    result = balancingPlot.check_human_decision()

                # report evaluated as incorrect
                if result == 1:
                    print("CLASSES ARE NOT BALANCED")
                    jsonIO.send_timestamp(time.time(), "end")
                    jsonIO.send_restart_configuration()
                    open('data/stop&go.json', 'w').close()
                    continue
                elif result == 2:
                    print("ERROR READING BALANCING REPORT FILE")
                    open('data/stop&go.json', 'w').close()
                    continue

                prepared_session = PreparedSessionManager(self._parameters.get_session_number())
                normalized_data = prepared_session.normalize_data()  # data modelling to enrich plot visibility

                # generate coverage plot
                radarPlot = CoverageReportRadarPlotView(self._parameters.get_session_number())
                radarPlot.generate_coverage_plot(normalized_data)
                print("COVERAGE REPORT GENERATED")

                if service_flag is False:
                    break

            if service_flag is True or stop_and_go['human_task'] == "check_coverage_report":
                radarPlot = CoverageReportRadarPlotView(self._parameters.get_session_number())

                # if testing mode is on, start the simulation to check if classes are balanced
                if service_flag is True:
                    print("HUMAN SIMULATION: EVALUATE COVERAGE REPORT")
                    result = radarPlot.simulated_coverage_report()
                else:
                    print("HUMAN TASK: EVALUATE COVERAGE REPORT")
                    result = radarPlot.check_human_decision()

                if result == 1:
                    print("DISTRIBUTION NOT UNIFORM")
                    jsonIO.send_timestamp(time.time(), "end")
                    jsonIO.send_restart_configuration()
                    open('data/stop&go.json', 'w').close()
                    continue
                elif result == 2:
                    print("ERROR READING BALANCING REPORT FILE")
                    open('data/stop&go.json', 'w').close()
                    continue

                # create learning sets
                learning_sets = LearningSetSplitter(self._parameters.get_session_number(),
                                                    self._parameters.get_training_set_size(),
                                                    self._parameters.get_validation_set_size(),
                                                    self._parameters.get_testing_set_size())
                result = learning_sets.generate_learning_set()
                print("LEARNING SETS GENERATED")

                # send to development
                jsonIO.send_learning_sets(result)
                open('data/stop&go.json', 'w').close()
                print("LEARNING SETS SENT TO DEVELOPMENT")

            if stop_and_go is not None and stop_and_go['human_task'] != "check_balancing_report" \
                    and stop_and_go['human_task'] != "check_coverage_report":
                print("INVALID STOP&GO USER INPUT")
                break


if __name__ == '__main__':
    segregation_system = SegregationSystemController()
    segregation_system.run()
