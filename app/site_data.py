from dataclasses import dataclass, asdict
from typing import Dict, Optional

@dataclass
class SiteData:
    region: str
    name: int
    number: str
    code: str
    lat: float
    lon: float
    elevation: float
    type: int
    station_name: str
    station_wmo_code: str

    def match(self, pattern: Optional[Dict] = None) -> bool:

        if pattern is None:
            return True
        
        self_asdict = asdict(self)
        
        for key in pattern:
            if pattern[key] != self_asdict[key]:
                return False
        return True
