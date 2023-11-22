from typing import NoReturn

from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Grid
from textual.message import Message


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

    class QuitPressed(Message):
        pass

    class NextPressed(Message):
        pass

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
    def pressed_quit(self) -> NoReturn:
        self.post_message(self.QuitPressed())
        self.app.exit()

    @on(Button.Pressed, '#quit_screen_next')
    def pressed_quit(self) -> NoReturn:
        self.post_message(self.NextPressed())
        self.app.pop_screen()
