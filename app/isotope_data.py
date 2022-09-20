import pandas as pd

from app.site_data import SiteData
from typing import Dict, Optional


class IsotopeData:
    site: SiteData
    isotope: str
    data: pd.DataFrame

    def __init__(self, data: pd.DataFrame, column: str, site: SiteData) -> None:
        self.site = site
        self.isotope = column.split('_')[1]
        self.data = data[['Year', column]].rename(columns={column: 'Value'})
    
    def match(self, isotope: str, site_pattern: Optional[Dict] = None) -> bool:
        if self.isotope != isotope:
            return False
        
        if not self.site.match(site_pattern):
            return False
        
        return True
