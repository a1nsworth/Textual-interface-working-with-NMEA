from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import NoReturn, List

import textual
from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import TabbedContent, TabPane, Select, Button, Input
from textual_datepicker import DateSelect

from application.constants import FILE_PATHS, FORMATS
from data_tables.data_table import DataTableGPGGA, DataTableFormat
from plot_text_plots.plot_text_plot import PlotText, PlotTextGPGGA, PlotTextGPRMC
from plot.plot_creator import PlotArgsCreatorGPGGAGPRMC


class DataTab(TabPane):
    """Страница Данных"""
    DEFAULT_CSS = """    
        #data_container_grid {
            layout: grid;
            grid-size: 2 2;
            grid-gutter: 1 2;
        }

        #data_table_gppga {
            height: 100%;
            width: 100%;
        }

        #left_data_table_panel {
            row-span: 2;
            height: 100%;
            width: 100%;
            background: $panel;
            border: dodgerblue;
        }

        #data_right_top_container {
            layout: grid;
            grid-size: 2 2;
            grid-rows: 80% 20%;
            background: $panel;
            border: greenyellow;
        }

        #b_upd_container {
            column-span: 2;
            align: center middle;
        }

        #b_update_table {

        }

        #data_right_bottom_container {
            layout: grid;
            grid-size: 2;
            height: 100%;
            background: $panel;
            border: red;
        }

        #select_format_for_save_table {
            column-span: 2;
        }
        """

    class MainContentContainer(Container):
        """Контейнер Данных"""

        def __init__(self):
            super().__init__(id='main_content_container_data_tab')

        def compose(self) -> ComposeResult:
            with Container(id='data_container_grid'):
                with Container(id='left_data_table_panel'):
                    yield DataTableGPGGA()

                with Container(id='data_right_top_container'):
                    yield Select(options=[(s, s) for s in FILE_PATHS.values()],
                                 prompt='Выберите файл для вывода таблицы',
                                 id='select_file_for_output_table')
                    yield Select(options=[(s, s) for s in FORMATS.values()],
                                 prompt='Выберите формат',
                                 id='select_format_table')
                    with Container(id='b_upd_container'):
                        yield Button('Обновить таблицу', id='b_upd_table')

                with Container(id='data_right_bottom_container'):
                    yield Select(options=[('csv', 0), ('txt', 1), ('xlsx', 2)],
                                 prompt='Формат таблицы для сохранения',
                                 id='select_format_for_save_table')
                    yield Button('Выберите путь для сохранения', id="select_directory_data_table")
                    yield Input(placeholder='Путь для сохранения', id='path_to_save_table')

    class ErrorSelectPath(Message):
        pass

    class ErrorSelectFormat(Message):
        pass

    @dataclass
    class ErrorNoAvailableFormat(Message):
        format: str
        available_fmt: List[str]

    @dataclass
    class ErrorNoAvailableImplementation(Message):
        path: Path

    class SelectDirectory(Message):
        pass

    def __init__(self, title: str = 'Данные'):
        super().__init__(id='data_tab', title=title)

    def compose(self) -> ComposeResult:
        with TabPane(title=self._title):
            yield self.MainContentContainer()

    def show_selected_path(self, to_show: Path | None) -> NoReturn:
        self.query_one('#path_to_save_table', Input).value = "EMPTY" if to_show is None else str(to_show)

    @on(Button.Pressed, "#select_directory_data_table")
    def select_directory(self) -> NoReturn:
        """show the `SelectDirectory` dialog when the button is pushed."""
        self.post_message(self.SelectDirectory())

    @on(Button.Pressed, '#b_upd_table')
    def update_table(self) -> NoReturn:
        table = self.query_one(DataTableFormat)
        path_file = self.query_one('#select_file_for_output_table', Select)
        table_format = self.query_one('#select_format_table', Select)

        if table_format.value is None:
            self.post_message(self.ErrorSelectFormat())
            return
        if path_file.value is None:
            self.post_message(self.ErrorSelectPath())
            return

        if table_format.value not in table.BASE_DF.available_formats():
            self.post_message(self.ErrorNoAvailableFormat(table_format.value, table.BASE_DF.available_formats()))
            return
        if path_file.value != table.BASE_DF.path:
            self.post_message(self.ErrorNoAvailableImplementation(path_file.value))
            return

        table.clear(True)
        df = table.BASE_DF.get_df_by_key(table_format.value)
        table.add_columns(*df.columns.tolist())
        table.add_rows(df.values.tolist())


class PlotTab(TabPane):
    DEFAULT_CSS = """
            #container_tab_plot_gpgga {
                layout: grid;
                grid-size: 2 3;
                grid-columns: 70% 30%;
            }

            #container_tab_plot_gpgga Input {

            }

            #container_plot_gpgga {
                row-span: 3
            }

            #container_input_date_gpgga {
                align: center middle;
                width: 75%;
            }

            #container_right_gpgga {
                align: center middle;
            }

            #container_b_upd_gprmc_plot {
                align: center middle;
            }

            #container_tab_plot_gprmc {
                layout: grid;
                grid-size: 3 3;
                grid-columns: 3fr 1fr 1fr;
                grid-rows: 5fr 5fr 1fr;
                content-align: center middle;
            }

            #container_plot_gprmc {
                row-span: 3; 
            }

            #container_b_upd_gprmc_plot {
                column-span: 2;
                align: center middle;
            }
        """

    def __init__(self, title: str = 'Графики'):
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        with TabPane('Графики', id='tab_plots'):
            with TabbedContent():
                with TabPane(f"График файла: {list(FILE_PATHS.values())[0].split('/')[-1]}"):
                    with TabbedContent():
                        with TabPane(f"График формата GPGGA"):
                            with Container(id='container_tab_plot_gpgga'):
                                with Container(id='container_plot_gpgga'):
                                    yield PlotTextGPGGA(id='plot_gpgga')
                                with Container(id='container_right_gpgga'):
                                    with Container(id='container_input_date_gpgga'):
                                        yield Input(placeholder='Введите время начала (в формате: HH:MM:SS)',
                                                    id='time_begin_gpgga')
                                        yield Input(placeholder='Введите время окончания (в формате: HH:MM:SS)',
                                                    id='time_end_gpgga')

                                    with Container(id='container_b_upd_gpgga_plot'):
                                        yield Button('Обновить график', id='b_upd_gpgga_plot')
                        with TabPane(f"График формата GPRMC"):
                            with Container(id='container_tab_plot_gprmc'):
                                with Container(id='container_plot_gprmc'):
                                    yield PlotTextGPRMC(id='plot_gprmc')

                                with Container(id='data_select_gprmc_container_begin'):
                                    yield DateSelect(placeholder="Выберите дату начала",
                                                     format="YYYY-MM-DD",
                                                     picker_mount="#container_tab_plot_gpgga",
                                                     id='gprmc_date_selector_begin')
                                yield Input(placeholder='Введите время в формате: HH:MM:SS')

                                with Container(id='data_select_gprmc_container_end'):
                                    yield DateSelect(placeholder="Выберите дату окончания",
                                                     format="YYYY-MM-DD",
                                                     picker_mount="#container_tab_plot_gprmc")
                                yield Input(placeholder='Введите время в формате: HH:MM:SS')

                                with Container(id='container_b_upd_gprmc_plot'):
                                    yield Button('Обновить график', id='b_upd_gprmc_plot')

                with TabPane(f"График файла: {list(FILE_PATHS.values())[1].split('/')[-1]}"):
                    pass
                with TabPane(f"График файла: {list(FILE_PATHS.values())[2].split('/')[-1]}"):
                    pass

    @on(Button.Pressed, '#b_upd_gpgga_plot')
    def update_gpgga_plot(self) -> NoReturn:
        plt_text = self.query_one('#plot_gpgga', PlotText)
        date_time_begin = datetime.strptime(self.query_one('#time_begin_gpgga', Input).value, "%H:%M:%S")
        date_time_end = datetime.strptime(self.query_one('#time_end_gpgga', Input).value, "%H:%M:%S")

        plt_text.update(**PlotArgsCreatorGPGGAGPRMC.create_args_time_longitude_gpgga(date_time_begin, date_time_end))


class MainTabContent(TabbedContent):
    def __init__(self):
        super().__init__(id='main_tab_content')

    def compose(self) -> ComposeResult:
        with TabbedContent():
            yield DataTab()
            yield PlotTab()
