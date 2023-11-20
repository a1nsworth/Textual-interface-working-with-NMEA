from datetime import datetime
from typing import Any

from parsing.data import DataGPGGAGPRMC
import plotext as pltx


class PlotArgsCreatorGPGGAGPRMC:
    @staticmethod
    def __create_args(*, y_values: list, x_values: list, x_label: str, y_label: str, title: str):
        return {'y_values': y_values, 'x_values': x_values, 'x_label': x_label, 'y_label': y_label, 'title': title}

    @staticmethod
    def __create_arg_gpgga_time_latitude_longitude(plot_by_latitude: bool, time_begin: str,
                                                   time_end: str, df) -> dict[str | Any]:
        x_label = 'Широта' if plot_by_latitude else 'Долгота'
        y_label = 'Время'
        title = f"Зависимости Времени от {'Широты' if plot_by_latitude else 'Долготы'}, формат: GPGGA"

        ldf = df[(time_begin <= df['Time']) & (df['Time'] <= time_end)]
        y_values = ldf['Time']
        x_values = ldf['Latitude' if plot_by_latitude else 'Longitude'].tolist()

        return PlotArgsCreatorGPGGAGPRMC.__create_args(
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

        return PlotArgsCreatorGPGGAGPRMC.__create_args(
            x_values=x_values,
            x_label=x_label,
            y_values=y_values,
            y_label=y_label,
            title=title,
        )

    @staticmethod
    def create_args_time_longitude_gpgga(time_begin: str, time_end: str) -> dict[str | Any]:
        return PlotArgsCreatorGPGGAGPRMC.__create_arg_gpgga_time_latitude_longitude(
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
        return PlotArgsCreatorGPGGAGPRMC.__create_arg_gpgga_time_latitude_longitude(
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

        return PlotArgsCreatorGPGGAGPRMC.__create_args(
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
