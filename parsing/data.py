from abc import abstractmethod
import math

from patterns.singleton import Singleton
from application.constants import *

import pandas as pd


class Data(metaclass=Singleton):
    def __init__(self, path):
        self._path = path
        self._df_formats = None

    @property
    def path(self):
        return self._path

    @abstractmethod
    def available_formats(self):
        pass

    @abstractmethod
    def get_df_by_key(self, key: str):
        pass

    def get_class_by_path(self, path: str):
        return self if path == self._path else None


class DataGPGGAGPRMC(Data):
    def __init__(self, path: str = GPGGA_GPRMC_PATH):
        super().__init__(path)
        self._df = self.__get_parce_df(self._path)
        self._df_formats = {
            'GPGGA': self.__get_parse_gpgga(),
            'GPRMC': self.__get_parse_gprmc(),
        }

    @staticmethod
    def get_dec_degree(x):
        return math.modf(x)[1] // 100 + (math.modf(x)[1] % 100) / 60 + (math.modf(x)[0] * 60) / 3600

    def __latitude_and_longitude_to_dec(self, serial: pd.Series):
        return serial.copy(deep=True).apply(lambda x: float(x)).apply(self.get_dec_degree)

    @staticmethod
    def __get_parce_df(path: str):
        df = pd.read_csv(path, sep=',', names=
        ['Message ID', 'Time', 'Latitude', 'N/S', 'Longitude', 'E/W', 'Pos Fix', 'Satellites Used', 'HDOP',
         'MSL Altitude',
         'Units1', 'Geoid Separation', 'Units2', 'Age of Diff.Corr.', 'Checksum',
         ])
        df['Message ID'] = df['Message ID'].apply(lambda t: t[1:])
        return df

    def __get_parse_gpgga(self):
        gpgga = self._df[self._df['Message ID'] == 'GPGGA'].copy(deep=True)
        gpgga['Time'] = pd.to_datetime(gpgga['Time'], format='%H%M%S').astype(str).apply(
            lambda x: x.split(' ')[-1])
        gpgga['Latitude'] = gpgga['Latitude'].apply(lambda x: float(x))
        gpgga['Longitude'] = gpgga['Longitude'].apply(lambda x: float(x))

        gpgga['Latitude'] = gpgga['Latitude'].apply(self.get_dec_degree)
        gpgga['Longitude'] = gpgga['Longitude'].apply(self.get_dec_degree)

        gpgga['Latitude'] = self.__latitude_and_longitude_to_dec(gpgga['Latitude'])
        gpgga['Longitude'] = self.__latitude_and_longitude_to_dec(gpgga['Longitude'])

        return gpgga.reset_index(drop=True)

    def __get_parse_gprmc(self):
        gprmc = self._df[self._df['Message ID'] == 'GPRMC'].iloc[:, 0:13]
        gprmc = gprmc.loc[:, gprmc.columns != 'Geoid Separation']
        gprmc.columns = ['Message ID', 'Time', 'Status', 'Latitude', 'N/S', 'Longitude', 'E/W', 'Speed',
                         'Course',
                         'Date', 'Magnetic Variation', 'Checksum', ]
        gprmc['Date'] = pd.to_datetime(gprmc['Date'], format='%d%m%y')
        gprmc['Time'] = pd.to_datetime(gprmc['Time'], format='%H%M%S').astype(str).apply(
            lambda x: x.split(' ')[-1])
        gprmc.insert(1, 'DateTime', (gprmc['Date'].astype(str) + ' ' + gprmc['Time']))
        gprmc['DateTime'] = pd.to_datetime(gprmc['DateTime'])

        gprmc['Latitude'] = self.__latitude_and_longitude_to_dec(gprmc['Latitude'])
        gprmc['Longitude'] = self.__latitude_and_longitude_to_dec(gprmc['Longitude'])

        return gprmc.reset_index(drop=True)

    @property
    def df(self):
        return self._df

    @property
    def df_gpgga(self):
        return self._df_formats['GPGGA']

    @property
    def df_gprmc(self):
        return self._df_formats['GPRMC']

    def available_formats(self):
        return list(self._df_formats.keys())

    def get_df_by_key(self, key: str) -> pd.DataFrame | None:
        try:
            return self._df_formats[key]
        except KeyError:
            return None

    def get_class_by_path(self, path: str):
        return self if path == self.path else None


class DataGetterByPath(metaclass=Singleton):
    def __init__(self, data: list = None):
        self.data = [DataGPGGAGPRMC(GPGGA_GPRMC_PATH)] if data is None else data

    def get_data_class_by_path(self, path):
        for data in self.data:
            data_class = data.get_class_by_path(path)
            if data_class is not None:
                return data_class
        return None
