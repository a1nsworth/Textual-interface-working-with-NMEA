from abc import abstractmethod, ABCMeta
from typing import NoReturn

from textual.widgets import DataTable

from parsing.data import DataGPGGAGPRMC


class DataTableFormat(DataTable):
    __metaclass__ = ABCMeta

    BASE_DF = DataGPGGAGPRMC()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data_frame = None

    @abstractmethod
    def _setup_table(self) -> NoReturn:
        pass

    @property
    def df(self):
        return self._data_frame


class DataTableGPGGA(DataTableFormat):
    def __init__(self):
        super().__init__(id='data_table_gpgga', zebra_stripes=True)
        self._setup_table()

    def _setup_table(self) -> NoReturn:
        self.add_columns(*DataGPGGAGPRMC().df_gpgga.columns.tolist())
        self.add_rows(DataGPGGAGPRMC().df_gpgga.values.tolist())


class DataTableGPRMC(DataTable):
    def __init__(self):
        super().__init__(id='data_table_gprmc', zebra_stripes=True)
        self._setup_table()

    def _setup_table(self) -> NoReturn:
        self.add_columns(*DataGPGGAGPRMC().df_gpgga.columns.tolist())
        self.add_rows(DataGPGGAGPRMC().df_gpgga.values.tolist())
