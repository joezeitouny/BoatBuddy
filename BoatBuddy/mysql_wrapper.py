from typing import Union

from mysql.connector import connect, Error, MySQLConnection
from mysql.connector.pooling import PooledMySQLConnection

from BoatBuddy.log_manager import LogManager


class MySQLWrapperQueries:

    @staticmethod
    def create_event_table_query(database_name):
        query = f"""
                CREATE TABLE {database_name}.`event` (
                  `id` int NOT NULL AUTO_INCREMENT, 
                  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, 
                  `type` varchar(10) NOT NULL, 
                  `message` varchar(1000) NOT NULL,                    
                  PRIMARY KEY (`id`)
                )
                """
        return query

    @staticmethod
    def create_event_for_event_table_query(database_name, size_limit):
        query = f"""
                    CREATE EVENT {database_name}.`event_cleanup` ON SCHEDULE EVERY 1 MINUTE
                    DO BEGIN
                            DECLARE cnt INTEGER;
                            DECLARE min_id INTEGER;
                            DECLARE delta INTEGER;

                            SET cnt = (SELECT COUNT(*) FROM {database_name}.log);        
                            SET min_id = (SELECT MIN(id) FROM {database_name}.log);
                            IF cnt > {size_limit} THEN
                                SET delta = cnt - {size_limit};        	
                                DELETE FROM {database_name}.log WHERE id < min_id + delta;
                            END IF;
                    END;
                    """
        return query

    @staticmethod
    def create_log_table_query(database_name):
        query = f"""
                CREATE TABLE {database_name}.`log` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `type` varchar(100) NOT NULL,
                  `message` varchar(10000) NOT NULL,
                  PRIMARY KEY (`id`)
                )
                """
        return query

    @staticmethod
    def create_event_for_log_table_query(database_name, size_limit):
        query = f"""
                CREATE EVENT {database_name}.`log_cleanup` ON SCHEDULE EVERY 1 MINUTE
                DO BEGIN
                        DECLARE cnt INTEGER;
                        DECLARE min_id INTEGER;
                        DECLARE delta INTEGER;
                        
                        SET cnt = (SELECT COUNT(*) FROM {database_name}.log);        
                        SET min_id = (SELECT MIN(id) FROM {database_name}.log);
                        IF cnt > {size_limit} THEN
                            SET delta = cnt - {size_limit};        	
                            DELETE FROM {database_name}.log WHERE id < min_id + delta;
                        END IF;
                END;
                """
        return query

    @staticmethod
    def create_session_table_query(database_name):
        query = f"""
                CREATE TABLE {database_name}.`session` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `session_id` varchar(1000) NOT NULL,                  
                  `start_time_utc` datetime NOT NULL,
                  `start_time_local` datetime NOT NULL,
                  `end_time_utc` datetime NOT NULL,
                  `end_time_local` datetime NOT NULL,
                  `duration` varchar(100) NOT NULL,
                  `ss_start_location` varchar(200) DEFAULT NULL,
                  `ss_end_location` varchar(200) DEFAULT NULL,
                  `ss_start_gps_lat` varchar(100) DEFAULT NULL,
                  `ss_start_gps_lon` varchar(100) DEFAULT NULL,
                  `ss_end_gps_lat` varchar(100) DEFAULT NULL,
                  `ss_end_gps_lon` varchar(100) DEFAULT NULL,
                  `ss_distance` varchar(100) DEFAULT NULL,
                  `ss_heading` varchar(100) DEFAULT NULL,
                  `ss_avg_sog` varchar(100) DEFAULT NULL,
                  `nm_start_location` varchar(200) DEFAULT NULL,
                  `nm_end_location` varchar(200) DEFAULT NULL,
                  `nm_start_gps_lat` varchar(100) DEFAULT NULL,
                  `nm_start_gps_lon` varchar(100) DEFAULT NULL,
                  `nm_end_gps_lat` varchar(100) DEFAULT NULL,
                  `nm_end_gps_lon` varchar(100) DEFAULT NULL,
                  `nm_distance` varchar(100) DEFAULT NULL,
                  `nm_heading` varchar(100) DEFAULT NULL,
                  `nm_avg_wind_speed` varchar(100) DEFAULT NULL,
                  `nm_avg_wind_direction` varchar(100) DEFAULT NULL,
                  `nm_avg_water_temperature` varchar(100) DEFAULT NULL,
                  `nm_avg_depth` varchar(100) DEFAULT NULL,
                  `nm_avg_sog` varchar(100) DEFAULT NULL,
                  `nm_avg_sow` varchar(100) DEFAULT NULL,
                  `gx_batt_max_voltage` varchar(100) DEFAULT NULL,
                  `gx_batt_min_voltage` varchar(100) DEFAULT NULL,
                  `gx_batt_avg_voltage` varchar(100) DEFAULT NULL,
                  `gx_batt_max_current` varchar(100) DEFAULT NULL,
                  `gx_batt_avg_current` varchar(100) DEFAULT NULL,
                  `gx_batt_max_power` varchar(100) DEFAULT NULL,
                  `gx_batt_avg_power` varchar(100) DEFAULT NULL,
                  `gx_pv_max_power` varchar(100) DEFAULT NULL,
                  `gx_pv_avg_power` varchar(100) DEFAULT NULL,
                  `gx_pv_max_current` varchar(100) DEFAULT NULL,
                  `gx_pv_avg_current` varchar(100) DEFAULT NULL,
                  `gx_start_batt_max_voltage` varchar(100) DEFAULT NULL,
                  `gx_start_batt_min_voltage` varchar(100) DEFAULT NULL,
                  `gx_start_batt_avg_voltage` varchar(100) DEFAULT NULL,
                  `gx_ac_consumption_max` varchar(100) DEFAULT NULL,
                  `gx_ac_consumption_avg` varchar(100) DEFAULT NULL,
                  `gx_tank1_max_level` varchar(100) DEFAULT NULL,
                  `gx_tank1_min_level` varchar(100) DEFAULT NULL,
                  `gx_tank1_avg_level` varchar(100) DEFAULT NULL,
                  `gx_tank2_max_level` varchar(100) DEFAULT NULL,
                  `gx_tank2_min_level` varchar(100) DEFAULT NULL,
                  `gx_tank2_avg_level` varchar(100) DEFAULT NULL,
                  PRIMARY KEY (`id`)
                ) 
                """
        return query

    @staticmethod
    def create_session_entry_table_query(database_name):
        query = f"""
                    CREATE TABLE {database_name}.`session_entry` (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `session_id` varchar(1000) NOT NULL,
                      `time_utc` datetime NOT NULL,
                      `time_local` datetime NOT NULL,
                      `ss_gps_lat` varchar(100) DEFAULT NULL,
                      `ss_gps_lon` varchar(100) DEFAULT NULL,
                      `ss_location` varchar(200) DEFAULT NULL,
                      `ss_sog` varchar(100) DEFAULT NULL,
                      `ss_cog` varchar(100) DEFAULT NULL,
                      `ss_distance_from_last_entry` varchar(100) DEFAULT NULL,
                      `ss_cumulative_distance` varchar(100) DEFAULT NULL,
                      `nm_true_hdg` varchar(100) DEFAULT NULL,
                      `nm_tws` varchar(100) DEFAULT NULL,
                      `nm_twd` varchar(100) DEFAULT NULL,
                      `nm_aws` varchar(100) DEFAULT NULL,
                      `nm_awa` varchar(100) DEFAULT NULL,
                      `nm_gps_lat` varchar(100) DEFAULT NULL,
                      `nm_gps_lon` varchar(100) DEFAULT NULL,
                      `nm_water_temperature` varchar(100) DEFAULT NULL,
                      `nm_depth` varchar(100) DEFAULT NULL,
                      `nm_sog` varchar(100) DEFAULT NULL,
                      `nm_sow` varchar(100) DEFAULT NULL,
                      `nm_distance_from_last_entry` varchar(100) DEFAULT NULL,
                      `nm_cumulative_distance` varchar(100) DEFAULT NULL,
                      `gx_active_input_source` varchar(100) DEFAULT NULL,
                      `gx_grid1_power` varchar(100) DEFAULT NULL,
                      `gx_generator1_power` varchar(100) DEFAULT NULL,
                      `gx_ac_input1_voltage` varchar(100) DEFAULT NULL,
                      `gx_ac_input1_current` varchar(100) DEFAULT NULL,
                      `gx_ac_input1_frequency` varchar(100) DEFAULT NULL,
                      `gx_ve_bus_state` varchar(100) DEFAULT NULL,
                      `gx_ac_consumption` varchar(100) DEFAULT NULL,
                      `gx_batt_voltage` varchar(100) DEFAULT NULL,
                      `gx_batt_current` varchar(100) DEFAULT NULL,
                      `gx_batt_power` varchar(100) DEFAULT NULL,
                      `gx_batt_soc` varchar(100) DEFAULT NULL,
                      `gx_batt_state` varchar(100) DEFAULT NULL,
                      `gx_pv_power` varchar(100) DEFAULT NULL,
                      `gx_pv_current` varchar(100) DEFAULT NULL,
                      `gx_start_batt_voltage` varchar(100) DEFAULT NULL,
                      `gx_tank1_level` varchar(100) DEFAULT NULL,
                      `gx_tank1_type` varchar(100) DEFAULT NULL,
                      `gx_tank2_level` varchar(100) DEFAULT NULL,
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
                      `ss_sog` varchar(100) DEFAULT NULL,
                      `ss_cog` varchar(100) DEFAULT NULL,
                      `ss_distance_from_last_entry` varchar(100) DEFAULT NULL,
                      `ss_cumulative_distance` varchar(100) DEFAULT NULL,
                      `nm_true_hdg` varchar(100) DEFAULT NULL,
                      `nm_tws` varchar(100) DEFAULT NULL,
                      `nm_twd` varchar(100) DEFAULT NULL,
                      `nm_aws` varchar(100) DEFAULT NULL,
                      `nm_awa` varchar(100) DEFAULT NULL,
                      `nm_gps_lat` varchar(100) DEFAULT NULL,
                      `nm_gps_lon` varchar(100) DEFAULT NULL,
                      `nm_water_temperature` varchar(100) DEFAULT NULL,
                      `nm_depth` varchar(100) DEFAULT NULL,
                      `nm_sog` varchar(100) DEFAULT NULL,
                      `nm_sow` varchar(100) DEFAULT NULL,
                      `nm_distance_from_last_entry` varchar(100) DEFAULT NULL,
                      `nm_cumulative_distance` varchar(100) DEFAULT NULL,
                      `gx_active_input_source` varchar(100) DEFAULT NULL,
                      `gx_grid1_power` varchar(100) DEFAULT NULL,
                      `gx_generator1_power` varchar(100) DEFAULT NULL,
                      `gx_ac_input1_voltage` varchar(100) DEFAULT NULL,
                      `gx_ac_input1_current` varchar(100) DEFAULT NULL,
                      `gx_ac_input1_frequency` varchar(100) DEFAULT NULL,
                      `gx_ve_bus_state` varchar(100) DEFAULT NULL,
                      `gx_ac_consumption` varchar(100) DEFAULT NULL,
                      `gx_batt_voltage` varchar(100) DEFAULT NULL,
                      `gx_batt_current` varchar(100) DEFAULT NULL,
                      `gx_batt_power` varchar(100) DEFAULT NULL,
                      `gx_batt_soc` varchar(100) DEFAULT NULL,
                      `gx_batt_state` varchar(100) DEFAULT NULL,
                      `gx_pv_power` varchar(100) DEFAULT NULL,
                      `gx_pv_current` varchar(100) DEFAULT NULL,
                      `gx_start_batt_voltage` varchar(100) DEFAULT NULL,
                      `gx_tank1_level` varchar(100) DEFAULT NULL,
                      `gx_tank1_type` varchar(100) DEFAULT NULL,
                      `gx_tank2_level` varchar(100) DEFAULT NULL,
                      `gx_tank2_type` varchar(100) DEFAULT NULL,
                      `gps_plugin_status`  varchar(100) DEFAULT NULL,
                      `nmea_plugin_status`  varchar(100) DEFAULT NULL,
                      `victron_plugin_status`  varchar(100) DEFAULT NULL,
                      PRIMARY KEY (`id`)
                    )
                    """
        return query


class MySQLWrapper:
    def __init__(self, options, log_manager: LogManager):
        self._options = options
        self._log_manager = log_manager

    def connect_to_server(self) -> bool:
        try:
            with connect(
                    host=self._options.database_host,
                    user=self._options.database_user,
                    password=self._options.database_password,
            ):
                return True
        except Error as e:
            self._log_manager.debug(f'Could not connect to MySQL server. Details {e}')

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
                event_scheduler_query = f'SET GLOBAL event_scheduler = ON;'
                with connection.cursor() as cursor:
                    cursor.execute(create_db_query)
                    cursor.execute(MySQLWrapperQueries.create_event_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_log_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_session_entry_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_session_table_query(database_name))
                    cursor.execute(MySQLWrapperQueries.create_live_feed_entry_table_query(database_name))
                    if self._options.database_cleanup_events:
                        cursor.execute(event_scheduler_query)
                        cursor.execute(MySQLWrapperQueries.create_event_for_log_table_query(
                            database_name, self._options.database_log_table_limit))
                        cursor.execute(MySQLWrapperQueries.create_event_for_event_table_query(
                            database_name, self._options.database_event_table_limit))

            return True
        except Exception as e:
            self._log_manager.info(f'Could not initialize database \'{self._options.database_name}\'. Details {e}')
            return False

    def _connect_to_database(self) -> Union[PooledMySQLConnection, MySQLConnection]:
        try:
            connection = connect(
                host=self._options.database_host,
                user=self._options.database_user,
                password=self._options.database_password,
                database=self._options.database_name
            )

            return connection
        except Error as e:
            self._log_manager.debug(f'Could not connect to MySQL database. Details {e}')

        return Union[None]

    def add_entry(self, table_name, columns, values):
        if not columns or not values or len(columns) == 0 or len(values) == 0:
            raise ValueError('Columns and values arguments cannot be empty')

        # Build the insert query
        insert_query = f'INSERT INTO {self._options.database_name}.{table_name} ('

        count = 0
        insert_query_part2 = f') VALUES ('
        refined_values = []
        while count < len(columns):
            if values[count] != '':
                insert_query += f'{columns[count]},'
                insert_query_part2 += f'%s,'
                refined_values.append(values[count])
            count += 1
        insert_query = insert_query[:-1]
        insert_query_part2 = insert_query_part2[:-1]
        insert_query += insert_query_part2
        insert_query += f')'

        connection = self._connect_to_database()
        connection.cursor().execute(insert_query, refined_values)
        connection.commit()
        connection.cursor().close()
        connection.close()
