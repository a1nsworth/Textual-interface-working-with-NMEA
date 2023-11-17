from pathlib import Path

import pendulum
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Center, Grid, Horizontal
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, Label, Static, DataTable, Select, TabPane, TabbedContent, Button, \
    Input
from textual_fspicker import SelectDirectory
from plot.plot_creator import PlotCreatorGPRMC, PlotCreatorGPGGA

from application.constants import FILE_PATHS, FORMATS
from parsing.data import DataGPGGAGPRMC, Singleton
from textual_datepicker import DateSelect


# TODO Красивое оформление страницы Данные
class DataTableGPPGAGRMC(metaclass=Singleton):
    def __init__(self):
        self.__table_gpgga = DataTable(zebra_stripes=True, id='data_table_gppga')
        self.__table_gpgga.add_columns(*DataGPGGAGPRMC().df_gpgga.columns.tolist())
        self.__table_gpgga.add_rows(DataGPGGAGPRMC().df_gpgga.values.tolist())

        self.__table_gprmc = DataTable(zebra_stripes=True, id='data_table_gprmc')
        self.__table_gprmc.add_columns(*DataGPGGAGPRMC().df_gprmc.columns.tolist())
        self.__table_gprmc.add_rows(DataGPGGAGPRMC().df_gprmc.values.tolist())

    @property
    def table_gpgga(self):
        return self.__table_gpgga

    @property
    def table_gprmc(self):
        return self.__table_gprmc


class MyTabs(Static):
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

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane('Данные', id='tab_data'):
                with Container(id='data_container_grid'):
                    with Container(id='left_data_table_panel'):
                        yield DataTableGPPGAGRMC().table_gpgga

                    with Container(id='data_right_top_container'):
                        yield Select(options=[(s, s) for s in FILE_PATHS.values()],
                                     prompt='Выберите файл для вывода таблицы',
                                     id='select_file_for_output_table')
                        yield Select(options=[(s, s) for s in FORMATS.values()],
                                     prompt='Выберите формат',
                                     id='select_format_table')
                        with Container(id='b_upd_container'):
                            yield Button('Обновить таблицу', id='b_update_table')

                    with Container(id='data_right_bottom_container'):
                        yield Select(options=[('csv', 0), ('txt', 1), ('xlsx', 2)],
                                     prompt='Формат таблицы для сохранения',
                                     id='select_format_for_save_table')
                        yield Button('Выберите путь для сохранения', id="directory")
                        yield Input(placeholder='Путь для сохранения', id='path_to_save_table')

            with TabPane('Графики', id='tab_plots'):
                with TabbedContent():
                    with TabPane(f"График файла: {list(FILE_PATHS.values())[0].split('/')[-1]}"):
                        with TabbedContent():
                            with TabPane(f"График формата GPGGA"):
                                with Container(id='container_tab_plot_gpgga'):
                                    with Container(id='container_plot_gpgga'):
                                        yield PlotCreatorGPGGA().create_plot_latitude_longitude()
                                    with Container(id='container_right_gpgga'):
                                        with Container(id='container_input_date_gpgga'):
                                            yield Input(placeholder='Введите время начала (в формате: HH:MM:SS)')
                                            yield Input(placeholder='Введите время окончания (в формате: HH:MM:SS)')

                                        with Container(id='container_b_upd_gpgga_plot'):
                                            yield Button('Обновить график', id='b_upd_gpgga_plot')

                            with TabPane(f"График формата GPRMC"):
                                with Container(id='container_tab_plot_gprmc'):
                                    with Container(id='container_plot_gprmc'):
                                        yield PlotCreatorGPRMC().create_plot_latitude_longitude()

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


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""
    DEFAULT_CSS = """
        QuitScreen {
            align: center middle;
        }
        
        #quit_screen_dialog {
            grid-size: 2;
            grid-gutter: 1 2;
            grid-rows: 1fr 3;
            padding: 0 1;
            width: 60;
            height: 11;
            border: thick $background 80%;
            background: $surface;
        }
        
        #quit_screen_label_text {
            column-span: 2;
            height: 1fr;
            width: 1fr;
            content-align: center middle;
        }
        
        Button {
            width: 100%;
        }
    """

    def __init__(self, label: str):
        super().__init__()
        self.__label = label

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.__label, id="quit_screen_label_text"),
            Button("Выйти из приложения", variant="error", id="quit_screen_quit"),
            Button("Назад", variant="primary", id="quit_screen_next"),
            id="quit_screen_dialog",
        )

    @on(Button.Pressed, '#quit_screen_quit')
    def pressed_quit(self) -> None:
        self.app.exit()

    @on(Button.Pressed, '#quit_screen_next')
    def pressed_quit(self) -> None:
        self.app.pop_screen()


class Application(App):
    """A Textual app to manage stopwatches."""
    CSS = """
        Header {
              dock: top;
              height: 3;
              content-align: center middle;
        }
    """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield MyTabs()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def show_selected(self, to_show: Path | None) -> None:
        """Show the file that was selected by the user.

        Args:
            to_show: The file to show.
        """
        self.query_one('#path_to_save_table', Input).value = "EMPTY" if to_show is None else str(to_show)

    @on(Button.Pressed, "#directory")
    def select_directory(self) -> None:
        """show the `SelectDirectory` dialog when the button is pushed."""
        self.push_screen(SelectDirectory(), callback=self.show_selected)

    # TODO cделать класс который будет по значению format and path возвращать нужную таблицу
    @on(Button.Pressed, '#b_update_table')
    def _update_table(self):
        table = self.query_one(DataTable)
        path_file = self.query_one('#select_file_for_output_table', Select)
        table_format = self.query_one('#select_format_table', Select)

        if table_format.value is None:
            self.push_screen(QuitScreen('Выберите формат таблицы'))
        if path_file.value is None:
            self.push_screen(QuitScreen('Выберите файл для вывода таблицы'))
            return

        if table_format.value not in DataGPGGAGPRMC().available_formats():
            self.push_screen(QuitScreen(
                f'У этого файла нет такого формата.\nДоступные форматы: {DataGPGGAGPRMC().available_formats()}'))
        if path_file.value != DataGPGGAGPRMC().path:
            self.push_screen(QuitScreen(str(path_file.value)))
            return

        table.clear(True)
        df = DataGPGGAGPRMC().get_df_by_key(table_format.value)
        table.add_columns(*df.columns.tolist())
        table.add_rows(df.values.tolist())
