from sklearn.model_selection import train_test_split

from segregationsystem.session_storage import SessionStorage


class LearningSetSplitter:
    def __init__(self, session_number, training_size, validation_size, test_size):
        self._session_number = session_number
        self._training_size = training_size
        self._validation_size = validation_size
        self._test_size = test_size

    # split prepared sessions received into training, test e validation,
    # return json object to send at the developer
    def generate_learning_set(self):
        storage = SessionStorage()
        dataset = storage.load_prepared_session()     # get all prepared session stored
        dataset_size = self._session_number

        # get the number of prepared session that every set must have, read from config
        training_size = round(self._training_size*dataset_size)
        validation_size = round(self._validation_size*dataset_size)
        testing_size = round(self._test_size*dataset_size)

        # split data into training testing and validation
        training, res = train_test_split(dataset, train_size=training_size)
        testing, validation = train_test_split(res, train_size=testing_size)

        feature_names = ['maximum_powerconsumptiontimeseries', 'median_powerconsumptiontimeseries',
                         'skeweness_powerconsumptiontimeseries', 'meanabsolutedeviation_powerconsumptiontimeseries',
                         'tissue_product', 'load_and_speed_type', 'label']

        # crete json object, to be send at the development system
        training = [{feature: value for feature, value in zip(feature_names, sample[1:])} for sample in training]
        validation = [{feature: value for feature, value in zip(feature_names, sample[1:])} for sample in validation]
        testing = [{feature: value for feature, value in zip(feature_names, sample[1:])} for sample in testing]

        return {'content': "learning_sets", 'training_set': training, 'validation_set': validation, 'test_set': testing}
