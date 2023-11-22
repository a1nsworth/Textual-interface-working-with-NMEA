import math
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from parsing.data import DataGPGGAGPRMC, DataGPGSVGPRMCGPGSA
from application.constants import ALL_FORMATS_1_PATH, ALL_FORMATS_2_PATH


def create_args(*, y_values: list, x_values: list, x_label: str, y_label: str, title: str):
    return {'y_values': y_values, 'x_values': x_values, 'x_label': x_label, 'y_label': y_label, 'title': title}


class PlotArgsCreatorSatellites:
    @staticmethod
    def __create_data_satellites(df: pd.DataFrame):
        columns_azimuth = ['Azimuth1', 'Azimuth2', 'Azimuth3', 'Azimuth4']
        columns_elevation = ['Elevation1', 'Elevation2', 'Elevation3', 'Elevation4']

        azimuth_values = []
        elevation_values = []
        for i in range(len(columns_azimuth)):
            azimuth_values = np.append(azimuth_values, pd.to_numeric(df[columns_azimuth[i]]).to_numpy())
            elevation_values = np.append(elevation_values, pd.to_numeric(df[columns_elevation[i]]).to_numpy())

        x_values = []
        y_values = []
        for i in range(len(azimuth_values)):
            x_values = np.append(x_values, azimuth_values[i] * math.cos(math.radians(elevation_values[i])))
            y_values = np.append(y_values, azimuth_values[i] * math.sin(math.radians(elevation_values[i])))

        return x_values, y_values

    @staticmethod
    def create_args_data():
        x_values_1, y_values_1 = PlotArgsCreatorSatellites.__create_data_satellites(
            DataGPGSVGPRMCGPGSA(ALL_FORMATS_1_PATH)['GPGSV'])
        x_values_2, y_values_2 = PlotArgsCreatorSatellites.__create_data_satellites(
            DataGPGSVGPRMCGPGSA(ALL_FORMATS_2_PATH)['GPGSV'])

        return (x_values_1, y_values_1), (x_values_2, y_values_2)

    @staticmethod
    def create_data():
        x_y_1, x_y_2 = PlotArgsCreatorSatellites.create_args_data()
        return np.concatenate([x_y_1[0], x_y_2[0]]), np.concatenate([x_y_1[1], x_y_2[1]])


class PlotArgsCreatorGPGGAGPRMC:

    @staticmethod
    def __create_args_gpgga_time_latitude_longitude(plot_by_latitude: bool, time_begin: str,
                                                    time_end: str, df) -> dict[str | Any]:
        x_label = 'Широта' if plot_by_latitude else 'Долгота'
        y_label = 'Время'
        title = f"Зависимости Времени от {'Широты' if plot_by_latitude else 'Долготы'}, формат: GPGGA"

        ldf = df[(time_begin <= df['Time']) & (df['Time'] <= time_end)]
        y_values = ldf['Time'].tolist()
        x_values = ldf['Latitude' if plot_by_latitude else 'Longitude'].tolist()

        return create_args(
            x_values=x_values,
            x_label=x_label,
            y_values=y_values,
            y_label=y_label,
            title=title,
        )

    @staticmethod
    def __create_arg_gprmc_time_latitude_longitude(plot_by_latitude: bool, date_time_begin: datetime,
                                                   date_time_end: datetime, df) -> dict[str | Any]:
        x_label = 'Широта' if plot_by_latitude else 'Долгота'
        y_label = 'Время (ч)'
        title = f"Зависимости Времени от {'Широты' if plot_by_latitude else 'Долготы'}, формат: GPGGA"

        ldf = df[(date_time_begin <= df['DateTime']) & (df['DateTime'] <= date_time_end)]
        y_values = ldf['DateTime']
        x_values = ldf['Latitude' if plot_by_latitude else 'Longitude'].tolist()

        return create_args(
            x_values=x_values,
            x_label=x_label,
            y_values=y_values,
            y_label=y_label,
            title=title,
        )

    @staticmethod
    def create_args_time_longitude_gpgga(time_begin: str, time_end: str) -> dict[str | Any]:
        return PlotArgsCreatorGPGGAGPRMC.__create_args_gpgga_time_latitude_longitude(
            False,
            time_begin,
            time_end,
            DataGPGGAGPRMC()['GPGGA'])

    @staticmethod
    def create_args_time_longitude_gprmc(date_time_begin: datetime, date_time_end: datetime) -> dict[str | Any]:
        return PlotArgsCreatorGPGGAGPRMC.__create_arg_gprmc_time_latitude_longitude(
            False,
            date_time_begin,
            date_time_end,
            DataGPGGAGPRMC()['GPRMC'])

    @staticmethod
    def create_args_time_latitude_gpgga(time_begin: str, time_end: str) -> dict[str | Any]:
        return PlotArgsCreatorGPGGAGPRMC.__create_args_gpgga_time_latitude_longitude(
            True,
            time_begin,
            time_end,
            DataGPGGAGPRMC()['GPGGA'])

    @staticmethod
    def create_args_time_latitude_gprmc(date_time_begin: datetime, date_time_end: datetime) -> dict[str | Any]:
        return PlotArgsCreatorGPGGAGPRMC.__create_arg_gprmc_time_latitude_longitude(
            True,
            date_time_begin,
            date_time_end,
            DataGPGGAGPRMC()['GPRMC'])

    @staticmethod
    def __create_args_latitude_longitude(df) -> dict[str | Any]:
        x_label = 'Широта'
        y_label = 'Долгота'
        title = f'Зависимости Широты от Долготы, формат: GPGGA'

        y_values = df['Latitude'].tolist()
        x_values = df['Longitude'].tolist()

        return create_args(
            x_values=x_values,
            y_values=y_values,
            x_label=x_label,
            y_label=y_label,
            title=title,
        )

    @staticmethod
    def create_args_latitude_longitude_gpgga():
        return PlotArgsCreatorGPGGAGPRMC.__create_args_latitude_longitude(DataGPGGAGPRMC()['GPGGA'])

    @staticmethod
    def create_args_latitude_longitude_gprmc():
        return PlotArgsCreatorGPGGAGPRMC.__create_args_latitude_longitude(DataGPGGAGPRMC()['GPRMC'])
