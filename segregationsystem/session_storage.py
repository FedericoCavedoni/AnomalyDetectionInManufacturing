from database.database_manager import DatabaseManager


class SessionStorage:
    def __init__(self):
        self.__db = DatabaseManager("segregation.db")

    def remove_prepared_session(self, session_uuid):
        query = "DELETE FROM session WHERE uuid = " + str(session_uuid) + ";"
        self.__db.commit_query(query)

    def load_prepared_session(self):
        query = "SELECT * FROM session;"
        record_db = self.__db.select_query(query)
        return record_db

    def store_prepared_session(self, json_data):
        uuid_value = json_data["uuid"]
        median_power_consumption_value = float(json_data["median_power_consumption"])
        max_power_consumption_value = float(json_data["max_power_consumption"])
        skewness_power_consumption_value = float(json_data["skewness_power_consumption"])
        mean_absolute_deviation_value = float(json_data["mean_absolute_deviation_consumption"])
        tissue_product_value = float(json_data["tissue_product"])
        load_and_speed_type_value = float(json_data["load_and_speed_type"])
        label_value = float(json_data["label"])

        query = f"INSERT INTO session VALUES(\"{uuid_value}\",{median_power_consumption_value}, \
                {max_power_consumption_value},{skewness_power_consumption_value},{mean_absolute_deviation_value}, \
                {tissue_product_value},{load_and_speed_type_value},{label_value}) "
        self.__db.commit_query(query)

    def get_prepared_session_number(self):
        query = "SELECT COUNT(*) FROM session;"
        record_db = self.__db.select_single_return(query)
        return record_db

    def delete_prepared_sessions(self):
        query = "DELETE FROM session"
        self.__db.commit_query(query)
