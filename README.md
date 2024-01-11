ANOMALY DETECTION IN MANUFACTORING - SETUP AND USE MANUAL
  1) Clone the repo on each node of the factory
  2) Install the required packages using "pip install -r requirements.txt"
  3) For each system: in "configuration" directory there are the configuration parameters, modify them
  4) Inside "global_configuration.json" there are the ip addresses and ports used by the systems, modify and share the file with all the systems
  5) You are ready to start the factory: launch each system executing "\<system\>_orchestrator.py"
  6) During the execution using "stop and go" mode: for each system, the reports and plots are put inside "data" folder

For testing, launch "service_class.py" after having started all the other systems
