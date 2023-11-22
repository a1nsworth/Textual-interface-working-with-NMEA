import math
from abc import ABCMeta
from typing import NoReturn

from textual.events import Mount
from textual_plotext import PlotextPlot

from plot.plot_creator import PlotArgsCreatorGPGGAGPRMC, PlotArgsCreatorSatellites


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
    ) -> NoReturn:
        """Initialise the weather widget.

        Args:
            name: The name of the PlotText widget.
            id: The ID of the weather widget in the DOM.
            classes: The CSS classes of the plot widget.
            disabled: PlotText the plot widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._title = title
        self._unit = "Loading..."
        self._x_values: list = []
        self._y_values: list = []
        self.x_label = ''
        self.y_label = ''

    def _fill_plot(self):
        self.plt.plot(self._x_values, self._y_values)
        self.plt.grid(True)

    def _fill_plot_info(self):
        self.plt.title(self._title)
        self.plt.xlabel(self.x_label)
        self.plt.ylabel(self.y_label)

    def on_mount(self) -> NoReturn:
        self.plt.date_form('H:M:S')
        self._fill_plot_info()
        self._fill_plot()
        self.refresh()

    def replot(self) -> NoReturn:
        self.plt.clear_data()
        self._fill_plot()
        self.refresh()

    def update(self, **kwargs) -> NoReturn:
        self._x_values = kwargs['x_values']
        self._y_values = kwargs['y_values']
        self.x_label = kwargs['x_label']
        self.y_label = kwargs['y_label']

        self._fill_plot_info()
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
        super().__init__(title=title, name=name, id=id, classes=classes, disabled=disabled)

        kwargs = PlotArgsCreatorGPGGAGPRMC.create_args_latitude_longitude_gprmc()
        self._x_values = kwargs['x_values']
        self._y_values = kwargs['y_values']
        self.x_label = kwargs['x_label']
        self.y_label = kwargs['y_label']


class PlotTextGPRMC(PlotText):
    def __init__(self,
                 title: str = '',
                 *,
                 name: str | None = None,
                 id: str | None = None,  # pylint:disable=redefined-builtin
                 classes: str | None = None,
                 disabled: bool = False,
                 ):
        super().__init__(title=title, name=name, id=id, classes=classes, disabled=disabled)

        kwargs = PlotArgsCreatorGPGGAGPRMC.create_args_latitude_longitude_gprmc()
        self._x_values = kwargs['x_values']
        self._y_values = kwargs['y_values']
        self.x_label = kwargs['x_label']
        self.y_label = kwargs['y_label']


class SkyPlotSatellite(PlotText):
    def __init__(self,
                 title: str = '',
                 *,
                 name: str | None = None,
                 id: str | None = None,  # pylint:disable=redefined-builtin
                 classes: str | None = None,
                 disabled: bool = False,
                 ):
        super().__init__(title=title, name=name, id=id, classes=classes, disabled=disabled, )
        self._x_values, self._y_values = PlotArgsCreatorSatellites.create_data()

    @staticmethod
    def create_map() -> tuple[list[float], list[float]]:
        x, y = [], []

        for r in range(100, 401, 100):
            for i in range(0, 360, 2):
                x.append(r * math.cos(math.radians(i)))
                y.append(r * math.sin(math.radians(i)))
        return x, y

    def _fill_plot(self):
        self.plt.scatter(self._x_values, self._y_values, marker='o')
        self.plt.grid(True)
