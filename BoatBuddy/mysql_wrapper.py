from typing import Union

from mysql.connector import connect, Error, MySQLConnection, CMySQLConnection
from mysql.connector.pooling import PooledMySQLConnection

from BoatBuddy import utils


class MySQLWrapperQueries:

    @staticmethod
    def create_events_table_query(database_name):
        query = f"""
                CREATE TABLE {database_name}.`events` (
                  `id` int NOT NULL AUTO_INCREMENT, 
                  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, 
                  `type` varchar(10) NOT NULL, 
                  `name` varchar(200) NOT NULL, 
                  `details` varchar(1000) NOT NULL, 
                  PRIMARY KEY (`id`)
                )
                """
        return query

    @staticmethod
    def create_log_table_query(database_name):
        query = f"""
                CREATE TABLE {database_name}.`log` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `message` varchar(10000) NOT NULL,
                  PRIMARY KEY (`id`)
                )
                """
        return query

    @staticmethod
    def create_session_table_query(database_name):
        query = f"""
                CREATE TABLE {database_name}.`session` (
                  `id` varchar(200) NOT NULL,
                  `start_time_utc` datetime NOT NULL,
                  `start_time_local` datetime NOT NULL,
                  `end_time_utc` datetime NOT NULL,
                  `end_time_local` datetime NOT NULL,
                  `duration` int NOT NULL,
                  `ss_start_location` varchar(200) DEFAULT NULL,
                  `ss_end_location` varchar(200) DEFAULT NULL,
                  `ss_start_gps_lat` varchar(100) DEFAULT NULL,
                  `ss_start_gps_lon` varchar(100) DEFAULT NULL,
                  `ss_end_gps_lat` varchar(100) DEFAULT NULL,
                  `ss_end_gps_lon` varchar(100) DEFAULT NULL,
                  `ss_distance` float DEFAULT NULL,
                  `ss_heading` int DEFAULT NULL,
                  `ss_avg_sog` float DEFAULT NULL,
                  `nm_start_location` varchar(200) DEFAULT NULL,
                  `nm_end_location` varchar(200) DEFAULT NULL,
                  `nm_start_gps_lat` varchar(100) DEFAULT NULL,
                  `nm_start_gps_lon` varchar(100) DEFAULT NULL,
                  `nm_end_gps_lat` varchar(100) DEFAULT NULL,
                  `nm_end_gps_lon` varchar(100) DEFAULT NULL,
                  `nm_distance` float DEFAULT NULL,
                  `nm_heading` int DEFAULT NULL,
                  `nm_avg_wind_speed` float DEFAULT NULL,
                  `nm_avg_wind_direction` int DEFAULT NULL,
                  `nm_avg_water_temperature` float DEFAULT NULL,
                  `nm_avg_depth` float DEFAULT NULL,
                  `nm_avg_sog` float DEFAULT NULL,
                  `nm_avg_sow` float DEFAULT NULL,
                  `gx_batt_max_voltage` float DEFAULT NULL,
                  `gx_batt_min_voltage` float DEFAULT NULL,
                  `gx_batt_avg_voltage` float DEFAULT NULL,
                  `gx_batt_max_current` float DEFAULT NULL,
                  `gx_batt_avg_current` float DEFAULT NULL,
                  `gx_batt_max_power` float DEFAULT NULL,
                  `gx_batt_avg_power` float DEFAULT NULL,
                  `gx_pv_max_power` float DEFAULT NULL,
                  `gx_pv_avg_power` float DEFAULT NULL,
                  `gx_pv_max_current` float DEFAULT NULL,
                  `gx_pv_avg_current` float DEFAULT NULL,
                  `gx_start_batt_max_voltage` float DEFAULT NULL,
                  `gx_start_batt_min_voltage` float DEFAULT NULL,
                  `gx_start_batt_avg_voltage` float DEFAULT NULL,
                  `gx_ac_consumption_max` float DEFAULT NULL,
                  `gx_ac_consumption_avg` float DEFAULT NULL,
                  `gx_tank1_max_level` float DEFAULT NULL,
                  `gx_tank1_min_level` float DEFAULT NULL,
                  `gx_tank1_avg_level` float DEFAULT NULL,
                  `gx_tank2_max_level` float DEFAULT NULL,
                  `gx_tank2_min_level` float DEFAULT NULL,
                  `gx_tank2_avg_level` float DEFAULT NULL,
                  PRIMARY KEY (`id`)
                ) 
                """
        return query

    @staticmethod
    def create_session_entry_table_query(database_name):
        query = f"""
                    CREATE TABLE {database_name}.`session_entry` (
                      `id` varchar(200) NOT NULL,
                      `time_utc` datetime NOT NULL,
                      `time_local` datetime NOT NULL,
                      `ss_gps_lat` varchar(100) DEFAULT NULL,
                      `ss_gps_lon` varchar(100) DEFAULT NULL,
                      `ss_location` varchar(200) DEFAULT NULL,
                      `ss_sog` float DEFAULT NULL,
                      `ss_cog` int DEFAULT NULL,
                      `ss_distance_from_last_entry` float DEFAULT NULL,
                      `ss_cumulative_distance` float DEFAULT NULL,
                      `nm_true_hdg` int DEFAULT NULL,
                      `nm_tws` float DEFAULT NULL,
                      `nm_twd` int DEFAULT NULL,
                      `nm_aws` float DEFAULT NULL,
                      `nm_awa` int DEFAULT NULL,
                      `nm_gps_lat` varchar(100) DEFAULT NULL,
                      `nm_gps_lon` varchar(100) DEFAULT NULL,
                      `nm_water_temperature` float DEFAULT NULL,
                      `nm_depth` float DEFAULT NULL,
                      `nm_sog` float DEFAULT NULL,
                      `nm_sow` float DEFAULT NULL,
                      `nm_distance_from_last_entry` float DEFAULT NULL,
                      `nm_cumulative_distance` float DEFAULT NULL,
                      `gx_active_input_source` varchar(100) DEFAULT NULL,
                      `gx_grid1_power` float DEFAULT NULL,
                      `gx_generator1_power` float DEFAULT NULL,
                      `gx_ac_input1_voltage` float DEFAULT NULL,
                      `gx_ac_input1_current` float DEFAULT NULL,
                      `gx_ac_input1_frequency` float DEFAULT NULL,
                      `gx_ve_bus_state` varchar(100) DEFAULT NULL,
                      `gx_ac_consumption` float DEFAULT NULL,
                      `gx_batt_voltage` float DEFAULT NULL,
                      `gx_batt_current` float DEFAULT NULL,
                      `gx_batt_power` float DEFAULT NULL,
                      `gx_batt_soc` float DEFAULT NULL,
                      `gx_batt_state` varchar(100) DEFAULT NULL,
                      `gx_pv_power` float DEFAULT NULL,
                      `gx_pv_current` float DEFAULT NULL,
                      `gx_start_batt_voltage` float DEFAULT NULL,
                      `gx_tank1_level` int DEFAULT NULL,
                      `gx_tank1_type` varchar(100) DEFAULT NULL,
                      `gx_tank2_level` int DEFAULT NULL,
                      `gx_tank2_type` varchar(100) DEFAULT NULL,
                      PRIMARY KEY (`id`)
                    )
                """
        return query

    @staticmethod
    def create_live_feed_entry_table_query(database_name):
        query = f"""
                    CREATE TABLE {database_name}.`live_feed_entry` (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `time_utc` datetime NOT NULL,
                      `time_local` datetime NOT NULL,
                      `ss_gps_lat` varchar(100) DEFAULT NULL,
                      `ss_gps_lon` varchar(100) DEFAULT NULL,
                      `ss_location` varchar(200) DEFAULT NULL,
                      `ss_sog` float DEFAULT NULL,
                      `ss_cog` int DEFAULT NULL,
                      `ss_distance_from_last_entry` float DEFAULT NULL,
                      `ss_cumulative_distance` float DEFAULT NULL,
                      `nm_true_hdg` int DEFAULT NULL,
                      `nm_tws` float DEFAULT NULL,
                      `nm_twd` int DEFAULT NULL,
                      `nm_aws` float DEFAULT NULL,
                      `nm_awa` int DEFAULT NULL,
                      `nm_gps_lat` varchar(100) DEFAULT NULL,
                      `nm_gps_lon` varchar(100) DEFAULT NULL,
                      `nm_water_temperature` float DEFAULT NULL,
                      `nm_depth` float DEFAULT NULL,
                      `nm_sog` float DEFAULT NULL,
                      `nm_sow` float DEFAULT NULL,
                      `nm_distance_from_last_entry` float DEFAULT NULL,
                      `nm_cumulative_distance` float DEFAULT NULL,
                      `gx_active_input_source` varchar(100) DEFAULT NULL,
                      `gx_grid1_power` float DEFAULT NULL,
                      `gx_generator1_power` float DEFAULT NULL,
                      `gx_ac_input1_voltage` float DEFAULT NULL,
                      `gx_ac_input1_current` float DEFAULT NULL,
                      `gx_ac_input1_frequency` float DEFAULT NULL,
                      `gx_ve_bus_state` varchar(100) DEFAULT NULL,
                      `gx_ac_consumption` float DEFAULT NULL,
                      `gx_batt_voltage` float DEFAULT NULL,
                      `gx_batt_current` float DEFAULT NULL,
                      `gx_batt_power` float DEFAULT NULL,
                      `gx_batt_soc` float DEFAULT NULL,
                      `gx_batt_state` varchar(100) DEFAULT NULL,
                      `gx_pv_power` float DEFAULT NULL,
                      `gx_pv_current` float DEFAULT NULL,
                      `gx_start_batt_voltage` float DEFAULT NULL,
                      `gx_tank1_level` int DEFAULT NULL,
                      `gx_tank1_type` varchar(100) DEFAULT NULL,
                      `gx_tank2_level` int DEFAULT NULL,
                      `gx_tank2_type` varchar(100) DEFAULT NULL,
                      `gps_plugin_status`  varchar(100) DEFAULT NULL,
                      `nmea_plugin_status`  varchar(100) DEFAULT NULL,
                      `victron_plugin_status`  varchar(100) DEFAULT NULL,
                      PRIMARY KEY (`id`)
                    )
                    """
        return query


class MySQLWrapper:
    def __init__(self, options):
        self._options = options

    def connect_to_server(self) -> bool:
        try:
            with connect(
                    host=self._options.database_host,
                    user=self._options.database_user,
                    password=self._options.database_password,
            ):
                return True
        except Error as e:
            utils.get_logger().debug(f'Could not connect to MySQL server. Details {e}')

        return False

    def is_initialised(self) -> bool:
        with connect(
                host=self._options.database_host,
                user=self._options.database_user,
                password=self._options.database_password
        ) as connection:
            check_db_query = f'SHOW DATABASES LIKE \'{self._options.database_name}\';'
            with connection.cursor() as cursor:
                cursor.execute(check_db_query)
                value = cursor.fetchall()
                if len(value) > 0:
                    return True
                else:
                    return False

    def initialise(self):
        try:
            with connect(
                    host=self._options.database_host,
                    user=self._options.database_user,
                    password=self._options.database_password
            ) as connection:
                database_name = self._options.database_name
                create_db_query = f'CREATE DATABASE {database_name}'
                with connection.cursor() as cursor:
                    cursor.execute(create_db_query)
                    cursor.execute(MySQLWrapperQueries.create_events_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_log_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_session_entry_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_session_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_live_feed_entry_table_query(database_name))
            return True
        except Exception as e:
            utils.get_logger().info(f'Could not initialize database \'{self._options.database_name}\'. Details {e}')
            return False

    def _connect_to_database(self) -> Union[PooledMySQLConnection, MySQLConnection, CMySQLConnection]:
        try:
            with connect(
                    host=self._options.database_host,
                    user=self._options.database_user,
                    password=self._options.database_password,
                    database=self._options.database_name
            ) as connection:
                return connection
        except Error as e:
            utils.get_logger().debug(f'Could not connect to MySQL database. Details {e}')

        return Union[None]

    def add_entry(self, table_name, columns, values):
        if not columns or not values or len(columns) == 0 or len(values) == 0:
            raise ValueError('Columns and values arguments cannot be empty')

        # Build the insert query
        insert_query = f'INSERT INTO {self._options.database_name}.{table_name} ('

        for column in columns:
            insert_query += f'{column},'
        insert_query.removesuffix(',')
        insert_query += f') VALUES ('
        for value in values:
            insert_query += f'{value},'
        insert_query.removesuffix(',')
        insert_query += f')'

        connection = self._connect_to_database()
        connection.cursor().execute(insert_query)
        connection.close()

    def update_entry(self, table_name, columns, values):
        pass
