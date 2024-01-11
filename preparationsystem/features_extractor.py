import numpy as np
from statistics import median, mean
from scipy.stats import skew

from ingestionsystem import raw_session
from preparationsystem.feature import Feature
from preparationsystem.prepared_session import PreparedSession

"""
FEATURES:
median power consumption time series
max power consumption time series
skewness power consumption time series
mean absolute deviation consumption time series
tissue product --> "towel":1 "facial":2 "napkins":3 "handerchiefs":4 "toilet":5
load & speed type --> "heavy":1 "regular":2 "fast":3 "slow":4
"""


class FeaturesExtractor:
    def extract_features(self, raw_session: raw_session):
        # Extracting power consumption time series from the raw session
        power_vars = raw_session.get_power_management_record().get_power_vars()
        max_power = max(power_vars)
        median_power = median(power_vars)
        mean_power = mean(power_vars)
        skewness = skew(power_vars)
        if np.isnan(skewness):
            skewness = 0

        tissue = self.tissue_feature(raw_session.get_production_management_record().get_production_type())
        load_and_speed = self.load_and_speed_feature(raw_session.get_machine_management_record().get_level())
        prepared_session_features = {Feature("median_power_consumption", median_power),
                                     Feature("max_power_consumption", max_power),
                                     Feature("mean_absolute_deviation_consumption", mean_power),
                                     Feature("skewness_power_consumption", skewness),
                                     Feature("tissue_product", tissue), Feature("load_and_speed_type", load_and_speed)}
        prepared_session = PreparedSession(raw_session.get_uuid(), prepared_session_features, raw_session.get_label())
        return prepared_session

    def tissue_feature(self, tissue):
        if tissue == "towel":
            return 1
        elif tissue == "facial":
            return 2
        elif tissue == "napkins":
            return 3
        elif tissue == "handerchiefs":
            return 4
        elif tissue == "toilet":
            return 5

        return -1

    def load_and_speed_feature(self, load_and_speed):
        if load_and_speed == "heavy":
            return 1
        elif load_and_speed == "regular":
            return 2
        elif load_and_speed == "fast":
            return 3
        elif load_and_speed == "slow":
            return 4

        return -1
