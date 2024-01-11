import glob
import os
import shutil

import requests


class Utils:
    @staticmethod
    def delete_files_pattern(pattern):
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)

    @staticmethod
    def send_timestamp(system, ip, port, timestamp, phase):  # For testing purposes
        endpoint = "http://" + ip + ":" + str(port) + "/service/log_timestamp"
        message = {'system': system, 'phase': phase, 'timestamp': timestamp}
        requests.post(endpoint, json=message)
