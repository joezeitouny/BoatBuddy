import time


class LogEntry:

    def __init__(self, utc_time, local_time, heading, true_wind_speed, true_wind_direction,
                 apparent_wind_speed, apparent_wind_angle, gps_longitude, gps_latitude,
                 gps_elevation, water_temperature, depth, speed_over_ground, speed_over_water):
        self.utc_time = utc_time
        self.local_time = local_time
        self.heading = heading
        self.true_wind_speed = true_wind_speed
        self.true_wind_direction = true_wind_direction
        self.apparent_wind_speed = apparent_wind_speed
        self.apparent_wind_angle = apparent_wind_angle
        self.gps_longitude = gps_longitude
        self.gps_latitude = gps_latitude
        self.gps_elevation = gps_elevation
        self.water_temperature = water_temperature
        self.depth = depth
        self.speed_over_ground = speed_over_ground
        self.speed_over_water = speed_over_water

    def __str__(self):
        return self.comma_separated_values()

    def comma_separated_values(self):
        lon = self.gps_longitude.to_string("d%°%m%\'%S%\" %H")
        lat = self.gps_latitude.to_string("d%°%m%\'%S%\" %H")
        return f'{time.strftime("%Y-%m-%d %H:%M:%S", self.utc_time)}' + \
            f',{time.strftime("%Y-%m-%d %H:%M:%S", self.local_time)}' + \
            f',{self.heading},{self.true_wind_speed}' + \
            f',{self.true_wind_direction},{self.apparent_wind_speed},{self.apparent_wind_angle}' + \
            f',{lon},{lat}' + \
            f',{self.gps_elevation},{self.water_temperature},{self.depth},{self.speed_over_ground}' + \
            f',{self.speed_over_water}'

    def string_value_list(self):
        lon = self.gps_longitude.to_string("d%°%m%\'%S%\" %H")
        lat = self.gps_latitude.to_string("d%°%m%\'%S%\" %H")
        return [f'{time.strftime("%Y-%m-%d %H:%M:%S", self.utc_time)}',
                f'{time.strftime("%Y-%m-%d %H:%M:%S", self.local_time)}',
                f'{self.heading}', f'{self.true_wind_speed}',
                f'{self.true_wind_direction}', f'{self.apparent_wind_speed}', f'{self.apparent_wind_angle}', lon, lat,
                f'{self.gps_elevation}', f'{self.water_temperature}', f'{self.depth}', f'{self.speed_over_ground}',
                f'{self.speed_over_water}']

    def get_utc_timestamp(self):
        return self.utc_time

    def get_local_timestamp(self):
        return self.local_time

    def get_heading(self):
        return self.heading

    def get_true_wind_speed(self):
        return self.true_wind_speed

    def get_true_wind_direction(self):
        return self.true_wind_direction

    def get_apparent_wind_speed(self):
        return self.apparent_wind_speed

    def get_apparent_wind_angle(self):
        return self.apparent_wind_angle

    def get_gps_longitude(self):
        return self.gps_longitude

    def get_gps_latitude(self):
        return self.gps_latitude

    def get_gps_elevation(self):
        return self.gps_elevation

    def get_water_temperature(self):
        return self.water_temperature

    def get_depth(self):
        return self.depth

    def get_speed_over_ground(self):
        return self.speed_over_ground

    def get_speed_over_water(self):
        return self.speed_over_water
