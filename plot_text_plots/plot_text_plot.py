from abc import ABCMeta, abstractmethod
from typing import NoReturn

from textual_plotext import PlotextPlot

from plot.plot_creator import PlotArgsCreatorGPGGAGPRMC


class PlotText(PlotextPlot):
    __metaclass__ = ABCMeta

    def __init__(
            self,
            title: str = '',
            *,
            name: str | None = None,
            id: str | None = None,  # pylint:disable=redefined-builtin
            classes: str | None = None,
            disabled: bool = False,
            x_values: list | None = None,
            y_values: list | None = None,

    ) -> NoReturn:
        """Initialise the weather widget.

        Args:
            name: The name of the weather widget.
            id: The ID of the weather widget in the DOM.
            classes: The CSS classes of the weather widget.
            disabled: Whether the weather widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._title = title
        self._unit = "Loading..."
        self._x_values = x_values
        self._y_values = y_values

    @abstractmethod
    def on_mount(self) -> NoReturn:
        self.plt.date_form('H:M:S')
        self.plt.title(self._title)
        self.plt.grid(True)
        self.plt.xlabel('Широта')
        self.plt.ylabel('Долгота')
        self.plt.plot(self._x_values, self._y_values)
        self.refresh()

    @abstractmethod
    def replot(self):
        self.plt.clear_data()
        self.plt.plot(self._x_values, self._y_values)
        self.refresh()

    @abstractmethod
    def update(self, **kwargs) -> NoReturn:
        self._x_values = kwargs['x_values']
        self._y_values = kwargs['y_values']
        self.plt.ylabel(kwargs['y_label'])
        self.plt.xlabel(kwargs['x_label'])
        self.replot()

    @abstractmethod
    def _watch_marker(self) -> None:
        """React to the marker being changed."""
        self.replot()


class PlotTextGPGGA(PlotText):
    def __init__(self,
                 title: str = '',
                 *,
                 name: str | None = None,
                 id: str | None = None,  # pylint:disable=redefined-builtin
                 classes: str | None = None,
                 disabled: bool = False,
                 ):
        kwargs = PlotArgsCreatorGPGGAGPRMC.create_args_latitude_longitude_gpgga()
        super().__init__(title=title, name=name, id=id, classes=classes, disabled=disabled, x_values=kwargs['x_values'],
                         y_values=kwargs['y_values'])


class PlotTextGPRMC(PlotText):
    def __init__(self,
                 title: str = '',
                 *,
                 name: str | None = None,
                 id: str | None = None,  # pylint:disable=redefined-builtin
                 classes: str | None = None,
                 disabled: bool = False,
                 ):
        kwargs = PlotArgsCreatorGPGGAGPRMC.create_args_latitude_longitude_gprmc()
        super().__init__(title=title, name=name, id=id, classes=classes, disabled=disabled, x_values=kwargs['x_values'],
                         y_values=kwargs['y_values'])
