from abc import abstractmethod, ABCMeta
from typing import NoReturn

from textual.widgets import DataTable

from parsing.data import DataGPGGAGPRMC, DataGPGSVGPRMCGPGSA
from patterns.singleton import Singleton
from application.constants import ALL_FORMATS_1_PATH, ALL_FORMATS_2_PATH, GPGGA_GPRMC_PATH


class DataTableFormat(DataTable):
    __metaclass__ = ABCMeta

    BASE_DF = DataGPGGAGPRMC()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data_frame = None
        self._path = None

    @abstractmethod
    def _setup_table(self) -> NoReturn:
        pass

    @property
    def df(self):
        return self._data_frame

    @df.setter
    def df(self, df):
        self._data_frame = df


class DataTableGPGGA(DataTableFormat):
    def __init__(self, id: str):
        super().__init__(id=id, zebra_stripes=True)
        self._data_frame = DataGPGGAGPRMC()
        self._setup_table()

    def _setup_table(self) -> NoReturn:
        self.add_columns(*self._data_frame['GPGGA'].columns.tolist())
        self.add_rows(self._data_frame['GPGGA'].values.tolist())


class DataTableGPRMC(DataTableFormat):
    def __init__(self, id: str = 'data_table_gprmc'):
        super().__init__(id=id, zebra_stripes=True)
        self._data_frame = DataGPGGAGPRMC()
        self._path = GPGGA_GPRMC_PATH
        self._setup_table()

    def _setup_table(self) -> NoReturn:
        self.add_columns(*self._data_frame['GPRMC'].columns.tolist())
        self.add_rows(self._data_frame['GPRMC'].values.tolist())


class DataTableGPGSVGPRMCGPGSA(DataTableFormat):
    def __init__(self, path: str, id='data_table_gpgsvgprmcgpgsa'):
        super().__init__(id=id, zebra_stripes=True)
        self._path = path
        self._data_frame = DataGPGSVGPRMCGPGSA(path=self._path)
        self._setup_table()

    def _setup_table(self) -> NoReturn:
        self.add_columns(*self._data_frame['GPGSV'].columns.tolist())
        self.add_rows(self._data_frame['GPGSV'].values.tolist())
