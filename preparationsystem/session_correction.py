# Class to perform correction operations on raw session data
# Interpolation of the missing samples of power time series
# Correction of the missing sample of the static records using the last value received
# Detection and correction of outliers in the power time series


class SessionCorrection:
    def correct_missing_samples_time_series(self, power):
        # Correct missing samples in a time series by interpolating values
        for channel in range(len(power)):
            if not power[channel]:
                left_index = channel - 1
                right_index = channel + 1

                while left_index >= 0 and not power[left_index]:
                    left_index -= 1

                while right_index < len(power) and not power[right_index]:
                    right_index += 1

                if left_index < 0:
                    power[channel] = float(power[right_index])
                elif right_index >= len(power):
                    power[channel] = float(power[left_index])
                else:
                    left_value = float(power[left_index])
                    right_value = float(power[right_index])
                    power[channel] = (left_value + right_value) / 2
            else:
                power[channel] = float(power[channel])

    def correct_missing_samples_static_records(self, record_vars, lasts_values):
        # Correct missing samples in static records by filling with the last values received
        for i in range(0, len(record_vars)):
            if record_vars[i] == "":
                record_vars[i] = lasts_values[i]
            else:
                lasts_values[i] = record_vars[i]

    def detect_and_correct_absolute_outliers(self, power, max_value, min_value):
        # Detect and correct absolute outliers in a time series by setting them to the maximum or minimum value
        for i, channel in enumerate(power):
            if channel > max_value:
                power[i] = max_value
            elif channel < min_value:
                power[i] = min_value
