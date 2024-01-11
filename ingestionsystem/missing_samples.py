

class MissingSamples:
    def __init__(self):
        # Constructor to initialize the MissingSamples object with zero missing samples
        self.__number_of_missing_samples = 0

    def get_number_of_missing_samples(self):
        # Getter method to retrieve the number of missing samples
        return self.__number_of_missing_samples

    def set_number_of_missing_samples(self, number_of_missing_samples):
        # Setter method to update the number of missing samples
        self.__number_of_missing_samples = number_of_missing_samples

    def mark_missing_samples(self, samples_list, static_records_arrived):
        # Method to mark missing samples based on provided lists representing the power time series and the other
        # records arrived
        # Increment the number_of_missing_samples for each missing sample in samples_list (power time series)
        for i in range(0, len(samples_list)):
            if not samples_list[i]:
                self.__number_of_missing_samples += 1

        # Increment missing samples for each missing static record in static_records_arrived (machine, production)
        for i in range(0, len(static_records_arrived)):
            if not static_records_arrived[i]:
                self.__number_of_missing_samples += 1
