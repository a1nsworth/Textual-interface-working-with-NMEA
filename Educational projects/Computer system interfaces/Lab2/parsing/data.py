from abc import abstractmethod
import math
from datetime import datetime
from typing import NoReturn

import pytz

import numpy

from patterns.singleton import Singleton
from application.constants import *

import pandas as pd


def get_dec_degree(x):
    return math.modf(x)[1] // 100 + (math.modf(x)[1] % 100) / 60 + (math.modf(x)[0] * 60) / 3600


class Data:
    def __init__(self, path: str, df_formats: dict[str: pd.DataFrame] | None = None):
        self._path = path
        self._df_formats = df_formats

    @property
    def path(self):
        return self._path

    @abstractmethod
    def available_formats(self):
        pass

    @abstractmethod
    def __getitem__(self, item: str) -> pd.DataFrame | None:
        try:
            return self._df_formats[item]
        except KeyError:
            return None

    @abstractmethod
    def get_df_by_key(self, key: str):
        pass

    def get_class_by_path(self, path: str):
        return self if path == self._path else None


class DataGPGGAGPRMC(Data, metaclass=Singleton):
    def __init__(self, path: str = GPGGA_GPRMC_PATH):
        super().__init__(path)
        self._df = self.__get_parce_df(self._path)
        self._df_formats = {
            'GPGGA': self.__get_parse_gpgga(),
            'GPRMC': self.__get_parse_gprmc(),
        }

    def __latitude_and_longitude_to_dec(self, serial: pd.Series):
        return serial.copy(deep=True).apply(lambda x: float(x)).apply(get_dec_degree)

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
        series_to_date_time = pd.to_datetime(gpgga['Time'], format='%H%M%S')
        gpgga['DateTime'] = series_to_date_time
        gpgga['Time'] = series_to_date_time.astype(str).apply(
            lambda x: x.split(' ')[-1])

        gpgga['Latitude'] = gpgga['Latitude'].apply(lambda x: float(x))
        gpgga['Longitude'] = gpgga['Longitude'].apply(lambda x: float(x))

        gpgga['Latitude'] = gpgga['Latitude'].apply(get_dec_degree)
        gpgga['Longitude'] = gpgga['Longitude'].apply(get_dec_degree)

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
    def df_formats(self):
        return self._df_formats

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


class DataGPGSVGPRMCGPGSA(Data):
    def __init__(self, path: str = ALL_FORMATS_1_PATH):
        super().__init__(path)
        self._df = self.__get_parse_from_csv()
        self._df_formats = {
            'GPGGA': self.__get_parse_gpgga(),
            'GPRMC': self.__get_parse_gprmc(),
            'GPGSV': self.__get_parse_gpgsv(),
            'GPGSA': self.__get_parse_gpgsa(),
        }

    @staticmethod
    def __parsing_datatype_gpgsv(df: pd.DataFrame):
        # parsing with the processing of cases when we do not have all 4 channels (1-3 channels)
        # also edit data in the checksum
        for row in range(len(df)):
            # if we have 4 channels
            if df.iloc[row, 19] is not numpy.nan:
                # data like aa*bb => aa locate in SNR, bb locate in Checksum
                if str(df.iloc[row, 19])[0] == '*':
                    df.iloc[row, 20] = str(df.iloc[row, 19])
                    df.iloc[row, 19] = numpy.nan
                else:
                    df.iloc[row, 20] = '*' + str(df.iloc[row, 19]).split('*')[1]
                    df.iloc[row, 19] = str(df.iloc[row, 19]).split('*')[0]
            # if we have 3 channels
            elif df.iloc[row, 15] is not numpy.nan:
                if str(df.iloc[row, 15])[0] == '*':
                    df.iloc[row, 20] = str(df.iloc[row, 15])
                    df.iloc[row, 15] = numpy.nan
                else:
                    df.iloc[row, 20] = '*' + str(df.iloc[row, 15]).split('*')[1]
                    df.iloc[row, 15] = str(df.iloc[row, 15]).split('*')[0]
            # if we have 2 channels
            elif df.iloc[row, 11] is not numpy.nan:
                if str(df.iloc[row, 11])[0] == '*':
                    df.iloc[row, 20] = str(df.iloc[row, 11])
                    df.iloc[row, 11] = numpy.nan
                else:
                    df.iloc[row, 20] = '*' + str(df.iloc[row, 11]).split('*')[1]
                    df.iloc[row, 11] = str(df.iloc[row, 11]).split('*')[0]
            # if we have only one channels
            elif df.iloc[row, 7] is not numpy.nan:
                if str(df.iloc[row, 7])[0] == '*':
                    df.iloc[row, 20] = str(df.iloc[row, 7])
                    df.iloc[row, 7] = numpy.nan
                else:
                    df.iloc[row, 20] = '*' + str(df.iloc[row, 7]).split('*')[1]
                    df.iloc[row, 7] = str(df.iloc[row, 7]).split('*')[0]

    def __convert_data_gpgga(self, df: pd.DataFrame) -> NoReturn:
        df['Latitude'] = pd.to_numeric(df['Latitude']).apply(lambda x: get_dec_degree(x))
        df['Longitude'] = pd.to_numeric(df['Longitude']).apply(lambda x: get_dec_degree(x))
        df['Time'] = pd.to_numeric(df['Time']).apply(lambda s: self.get_time_as_seconds(str(s)))
        df['HDOP'] = pd.to_numeric(df['HDOP'])

    def __convert_data_gprmc(self, df: pd.DataFrame) -> NoReturn:
        df['Latitude'] = pd.to_numeric(df['Latitude']).apply(lambda x: get_dec_degree(x))
        df['Longitude'] = pd.to_numeric(df['Longitude']).apply(lambda x: get_dec_degree(x))
        df['Time'] = pd.to_numeric(df['Time']).apply(lambda s: self.get_time_as_seconds(s))
        df['Speed'] = pd.to_numeric(df['Speed'])

        # edit Magnetic and Checksum data
        df['Magnetic'] = df['Checksum'].apply(lambda x: x.split('*')[0])
        df['Checksum'] = '*' + df['Checksum'].apply(lambda x: x.split('*')[1])

    @staticmethod
    def get_time_as_seconds(x):
        t = str(x)
        if t[5] == '.':
            t = '0' + t

        return int(t[0] + t[1]) * 3600 + int(t[2] + t[3]) * 60 + int(t[4] + t[5])

    def __get_parse_from_csv(self):
        df = pd.read_csv(self.path, sep=',',
                         names=['Message ID', 'Number of Messages', 'Message Number', 'Satellites in View',
                                'Satellite ID1',
                                'Elevation1', 'Azimuth1', 'SNR1', 'Satellite ID2', 'Elevation2', 'Azimuth2', 'SNR2',
                                'Satellite ID3', 'Elevation3', 'Azimuth3', 'SNR3', 'Satellite ID4', 'Elevation4',
                                'Azimuth4',
                                'SNR4', 'Checksum'])
        df['Message ID'] = df['Message ID'].apply(lambda t: t[1:])
        return df

    def __get_parse_gpgsv(self) -> pd.DataFrame:
        df = self._df[self._df[self._df.columns[0]] == 'GPGSV'].copy()
        self.__parsing_datatype_gpgsv(df)

        columns_name = ['Azimuth1', 'Azimuth2', 'Azimuth3', 'Azimuth4', 'Elevation1', 'Elevation2', 'Elevation3',
                        'Elevation4']
        for name in columns_name:
            df[name] = pd.to_numeric(df[name])

        return df

    def __get_parse_gpgga(self) -> pd.DataFrame:
        df = self._df[self._df[self._df.columns[0]] == 'GPGGA'].iloc[:, 0:15]
        df.columns = ['Message ID', 'Time', 'Latitude', 'N/S', 'Longitude', 'E/W', 'Position', 'Satellites', 'HDOP',
                      'MSL Altitude', 'Units1', 'Geoid', 'Units2', 'Station ID', 'Checksum']
        self.__convert_data_gpgga(df)
        return df

    def __get_parse_gprmc(self) -> pd.DataFrame:
        df = self._df[self._df[self._df.columns[0]] == 'GPRMC'].iloc[:, 0:13].copy()
        df.iloc[:, 11] = df.iloc[:, 12]
        df = df.iloc[:, 0:12]
        df.columns = ['Message ID', 'Time', 'Status', 'Latitude', 'N/S', 'Longitude', 'E/W', 'Speed',
                      'Course', 'Date', 'Magnetic', 'Checksum']

        self.__convert_data_gprmc(df)
        return df

    def __get_parse_gpgsa(self) -> pd.DataFrame:
        df = self._df[self._df[self._df.columns[0]] == 'GPGSA'].iloc[:, 0:19].copy()
        df.iloc[:, 18] = df.iloc[:, 17]
        df.columns = ['Message ID', 'Mode1', 'Mode2', 'Satellite Used1', 'Satellite Used2', 'Satellite Used3',
                      'Satellite Used4', 'Satellite Used5', 'Satellite Used6', 'Satellite Used7', 'Satellite Used8',
                      'Satellite Used9', 'Satellite Used10', 'Satellite Used11', 'Satellite Used12', 'PDOP', 'HDOP',
                      'VDOP', 'Checksum']

        df['VDOP'] = df['Checksum'].apply(lambda x: x.split('*')[0])
        df['Checksum'] = '*' + df['Checksum'].apply(lambda x: x.split('*')[1])

        return df

    def available_formats(self) -> list[str]:
        return list(self._df_formats.keys())

    def get_df_by_key(self, key: str):
        return self[key]


class DataGetterByPath(metaclass=Singleton):
    def __init__(self):
        self._data = [DataGPGGAGPRMC(), DataGPGSVGPRMCGPGSA(ALL_FORMATS_1_PATH),
                      DataGPGSVGPRMCGPGSA(ALL_FORMATS_2_PATH)]

    def __getitem__(self, item: str):
        for data in self._data:
            data_class = data.get_class_by_path(item)
            if data_class is not None:
                return data_class
        return None

    def get_data_class_by_path(self, path):
        return self[path]
