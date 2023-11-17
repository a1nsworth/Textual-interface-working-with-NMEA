from datetime import datetime
from textual_plotext import PlotextPlot

from patterns.singleton import Singleton
from parsing.data import DataGPGGAGPRMC, GPGGA_GPRMC_PATH


class PlotCreator:
    @staticmethod
    def create_plot(title: str, x_label: str, y_label: str, x_values: list, y_values: list, grid: bool = True):
        plt_text = PlotextPlot()
        plt_text.plt.xlabel(x_label)
        plt_text.plt.ylabel(y_label)
        plt_text.plt.title(title)
        plt_text.plt.plot(x_values, y_values)
        plt_text.plt.grid(grid)

        return plt_text


class PlotCreatorGPGGA:
    @staticmethod
    def create_plot_time_latitude_longitude(latitude: bool, time_begin: datetime, time_end: datetime):
        x_label = 'Ширина' if latitude else 'Долгота'
        y_label = 'Время (ч)'
        title = f"Зависимости Времени от {'Ширины' if latitude else 'Долготы'}, формат: GPGGA"

        df = DataGPGGAGPRMC(GPGGA_GPRMC_PATH).df_gpgga
        df = df[(time_begin <= df['DateTime']) & (df['DateTime'] <= time_end)]
        y_values = df['Time'].tolist()
        x_values = df['Latitude' if latitude else 'Longitude'].tolist()

        return PlotCreator.create_plot(title, x_label, y_label, x_values, y_values)

    @staticmethod
    def create_plot_time_longitude(time_begin: datetime, time_end: datetime):
        return PlotCreatorGPGGA.create_plot_time_latitude_longitude(False, time_begin, time_end)

    @staticmethod
    def create_plot_time_latitude(time_begin: datetime, time_end: datetime):
        return PlotCreatorGPGGA.create_plot_time_latitude_longitude(True, time_begin, time_end)

    @staticmethod
    def create_plot_latitude_longitude():
        x_label = 'Широта'
        y_label = 'Долгота'
        title = f'Зависимости Широты от Долготы, формат: GPGGA'

        df = DataGPGGAGPRMC(GPGGA_GPRMC_PATH).df_gpgga
        y_values = df['Latitude'].tolist()
        x_values = df['Longitude'].tolist()

        return PlotCreator.create_plot(title, x_label, y_label, x_values, y_values)


class PlotCreatorGPRMC:
    @staticmethod
    def create_plot_time_latitude_longitude(latitude: bool, *, time_begin: datetime = None, time_end: datetime = None):
        x_label = 'Ширина' if latitude else 'Долгота'
        y_label = 'Время (ч)'
        title = f"Зависимости Времени от {'Ширины' if latitude else 'Долготы'}, формат: GPGGA"

        df = DataGPGGAGPRMC(GPGGA_GPRMC_PATH).df_gprmc
        df = df[(time_begin <= df['DateTime']) & (df['DateTime'] <= time_end)]
        y_values = df['Time'].tolist()
        x_values = df['Latitude' if latitude else 'Longitude'].tolist()

        return PlotCreator.create_plot(title, x_label, y_label, x_values, y_values)

    @staticmethod
    def create_plot_time_longitude(time_begin: datetime, time_end: datetime):
        return PlotCreatorGPGGA.create_plot_time_latitude_longitude(False, time_begin, time_end)

    @staticmethod
    def create_plot_time_latitude(time_begin: datetime, time_end: datetime):
        return PlotCreatorGPGGA.create_plot_time_latitude_longitude(True, time_begin, time_end)

    @staticmethod
    def create_plot_latitude_longitude():
        x_label = 'Широта'
        y_label = 'Долгота'
        title = f'Зависимости Широты от Долготы, формат: GPRMC'

        df = DataGPGGAGPRMC(GPGGA_GPRMC_PATH).df_gprmc
        y_values = df['Latitude'].tolist()
        x_values = df['Longitude'].tolist()

        return PlotCreator.create_plot(title, x_label, y_label, x_values, y_values)

    @staticmethod
    def create_plot_time_speed():
        x_label = 'Время (ч)'
        y_label = 'Скорость (км)'
        title = f'Зависимости Времени от Скорости, формат: GPRMC'

        df = DataGPGGAGPRMC(GPGGA_GPRMC_PATH).df_gprmc
        y_values = df['Time'].tolist()
        x_values = df['Speed'].tolist()

        return PlotCreator.create_plot(title, x_label, y_label, x_values, y_values)
