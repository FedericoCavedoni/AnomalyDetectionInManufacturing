import random
import pandas as pd
import numpy as np

from segregationsystem.session_storage import SessionStorage


class PreparedSessionManager:
    def __init__(self, session_number):
        self._session_number = session_number

    # load from db all the prepared session received from the preparation system and check if the
    # number is equal with the configuration parameter, return true if so otherwise false
    def check_sufficient_session(self):
        # get number of prepared session already received stored in the db
        storage = SessionStorage()
        num_session = storage.get_prepared_session_number()

        # if the number is equal (or above) with the configuration parameters return true
        if num_session[0] >= self._session_number:
            return True
        return False

    # function that add small scatter to the categorical feature then dataset normalization in order to
    # get a better visualization in the radar plot, return the normalized dataset
    def normalize_data(self):
        storage = SessionStorage()
        dataset = storage.load_prepared_session()

        labels = ['uuid', 'max_power_consumption', 'median_power_consumption',
                  'skewness_power_consumption', 'mean_absolute_deviation_consumption',
                  'tissue_product', 'load_and_speed_type', 'label']

        # create pandas dataframe from labels and prepared session values stored in db
        pandas_dataset = pd.DataFrame(data=dataset, columns=labels)

        # add small scatter (used in radar plot)
        for index, row in pandas_dataset.iterrows():
            small_scatter = random.uniform(-0.2, 0.2)
            pandas_dataset.at[index, "tissue_product"] += small_scatter
            pandas_dataset.at[index, "load_and_speed_type"] += small_scatter

        numeric_columns = pandas_dataset.select_dtypes(include=np.number).columns
        # for each column get the min value
        min_values = pandas_dataset[numeric_columns].min()

        # verify if there are negative values
        negative_values = min_values[min_values < 0]

        # shift negative value then normalize
        if not negative_values.empty:
            for col in negative_values.index:
                pandas_dataset[col] -= min_values[col]

        # apply normalization techniques
        for column in pandas_dataset[numeric_columns].columns:
            pandas_dataset[column] = pandas_dataset[column] / pandas_dataset[column].abs().max()

        pandas_dataset[numeric_columns] = pandas_dataset[numeric_columns].astype(float)
        dataset = pandas_dataset.to_json(orient="records")
        dataset_list = pd.read_json(dataset, orient="records")

        return dataset_list
