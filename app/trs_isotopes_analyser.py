import pandas as pd

from app.isotope_data import IsotopeData
from app.site_data import SiteData
from matplotlib.figure import Figure, Axes
from typing import Dict, Optional, List, Tuple


class TRSIsotopesAnalyser:
    sites: List[SiteData]
    isotopes: List[IsotopeData]
    climate_data = Dict[str, Dict[str, pd.DataFrame]]
    
    def __init__(self, sites_path: str, isotopes_path: str, climate_path: str) -> None:
        self.sites = self._load_sites_(sites_path)
        self.isotopes = self._load_isotopes_(isotopes_path)
        self.climate_data = self._load_climate_(climate_path)
    
    def _load_sites_(self, path: str) -> List[SiteData]:
        result = []
        sites = self._load_dataframe_(path)
        if len(pd.unique(sites['Site code'])) != len(sites):
            raise Exception("Not every site codes are unique!")
        for _, row in sites.iterrows():
            result.append(SiteData(*row))
        return result
    
    def _load_isotopes_(self, path: str) -> List[IsotopeData]:
        result = []
        data =  self._load_dataframe_(path)
        for column in data.columns:
            try:
                site = self.__get_sites_by_pattern__({'code': column.split('_')[0]})[0]
                result.append(IsotopeData(data, column, site))
            except IndexError:
                continue
        return result
    
    @staticmethod
    def _load_dataframe_(path) -> pd.DataFrame:
        if path.lower().endswith('.xlsx') or path.lower().endswith('.xls'):
            return pd.read_excel(path)
        elif path.lower().endswith('csv'):
            return pd.read_csv(path)
        else:
            raise Exception(f"Wrong spreadsheet format: {path}")
    
    @staticmethod
    def _load_climate_(path: str) -> Dict[str, Dict[str, pd.DataFrame]]:
        return
    
    def __get_sites_by_pattern__(self, pattern: Dict) -> List[SiteData]:
        return list(filter(lambda s: s.match(pattern), self.sites))
    
    def __get_isotopes_by_pattern__(self, isotope, site_pattern: Optional[Dict]=None) -> List[IsotopeData]:
        return list(filter(lambda i: i.match(isotope, site_pattern), self.isotopes))
    