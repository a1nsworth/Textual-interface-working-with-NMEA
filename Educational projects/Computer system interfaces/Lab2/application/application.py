from pathlib import Path
from typing import NoReturn

from matplotlib import pyplot as plt
from textual import on
from textual.app import App, ComposeResult
from textual.message import Message
from textual.widgets import (
    Header, Footer, Button, Input
)
from textual_fspicker import SelectDirectory

from screens.screens import QuitScreen
from tab.tab_contents import MainTabContent, DataTab


# TODO Красивое оформление страницы Данные


class Application(App):
    CSS = """
        Header {
              dock: top;
              height: 3;
              content-align: center middle;
        }
    """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self):
        super().__init__()

    class SelectDirectoryPathSelected(Message):
        def __init__(self, path: Path | None):
            self.path = path
            super().__init__()

    def compose(self) -> ComposeResult:
        """Create child tab for the app."""
        yield Header()
        yield Footer()
        yield MainTabContent()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def show_selected_path(self, to_show: Path | None) -> NoReturn:
        self.query_one('#path_to_save_table', Input).value = "EMPTY" if to_show is None else str(to_show)

    @on(DataTab.SelectDirectory)
    def select_directory(self) -> NoReturn:
        self.push_screen(SelectDirectory(),
                         callback=self.show_selected_path)

    @on(DataTab.ErrorSelectFormat)
    def error_select_format(self) -> NoReturn:
        self.push_screen(QuitScreen('Выберите формат таблицы'))

    @on(DataTab.ErrorSelectPath)
    def error_select_path(self) -> NoReturn:
        self.push_screen(QuitScreen('Выберите файл для вывода таблицы'))

    @on(DataTab.ErrorNoAvailableFormat)
    def error_no_available_format(self, message: DataTab.ErrorNoAvailableFormat):
        self.push_screen(QuitScreen(
            f'У этого файла нет формата {message.format}.\n'
            f'Доступные форматы: {message.available_fmt}'))

    @on(DataTab.ErrorNoAvailableImplementation)
    def error_no_available_implementation(self, message: DataTab.ErrorNoAvailableImplementation):
        self.push_screen(QuitScreen(
            f'У файла {message.path} нет реализации'))

    @on(Button.Pressed, '#b_upd_gpgga_plot')
    def __update_gpgga_plot(self):
        pass
