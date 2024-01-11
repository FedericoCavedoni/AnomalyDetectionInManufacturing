import time
from threading import Thread

from service_class2 import ServiceClass, listener

service_class = ServiceClass.get_instance()



csv_lines_power = service_class.get_csv_file_lines("../data/powerManagementSys.csv")
csv_lines_production = service_class.get_csv_file_lines("../data/productionManagementSys.csv")
csv_lines_machine = service_class.get_csv_file_lines("../data/machineManagementSys.csv")
csv_lines_label = service_class.get_csv_file_lines("../data/labels.csv")


def send_records_client_sys(sessions_number: int):
    record_counter = 0
    while record_counter < sessions_number:
        service_class.send_records(csv_lines_power, csv_lines_production, csv_lines_machine, csv_lines_label)
        record_counter += 1
    print("END RECORDS")


if __name__ == '__main__':
    with open("log.log", "a") as f:
        f.write(str(time.time()) + ",Service Class,start \n")
    rest_server = Thread(target=listener)
    rest_server.setDaemon(True)
    rest_server.start()
    # sessions_number = int(sys.argv[1])
    sessions_number = 5050
    client_side_sys = Thread(target=lambda: send_records_client_sys(sessions_number))
    client_side_sys.setDaemon(True)
    client_side_sys.start()
    while True:
        print(service_class.recv_msg())  # Wait for 'start production' or 'restart'
        with open("log.log", "a") as f:
            f.write(str(time.time()) + ", Service Class, end \n")
    exit(0)

"""

import time
from multiprocessing import Process

def start_server():
    with open("log.log", "a") as f:
        f.write(str(time.time()) + ",Service Class,start \n")

    rest_server = Thread(target=listener)
    rest_server.setDaemon(True)
    rest_server.start()

    while True:
        print(service_class.recv_msg())  # Wait for 'start production' or 'restart'
        with open("log.log", "a") as f:
            f.write(str(time.time()) + ", Service Class, end \n")

def run_client(sessions_number):
    client_side_sys = Thread(target=lambda: send_records_client_sys(sessions_number))
    client_side_sys.setDaemon(True)
    client_side_sys.start()
    client_side_sys.join()

if __name__ == '__main__':
    server_process = Process(target=start_server)
    server_process.start()

    for sessions_number in range(1, 6):  # Esegui da 1 a 5 volte, puoi adattare il range secondo le tue esigenze
        print("SESSION: "+str(sessions_number))
        run_client(sessions_number)

    # Attendere che il processo del server termini prima di uscire
    server_process.join()

    exit(0)
    
"""