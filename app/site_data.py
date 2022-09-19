from dataclasses import dataclass, asdict


@dataclass
class SiteData:
    region: str
    number: int
    name: str
    code: str
    lat: float
    lon: float
    elevation: float
    type: int
    station_name: str
    station_wmo_code: str

    def match(self, pattern: dict) -> bool:
        self_asdict = asdict(self)
        for key in pattern:
            if pattern[key] != self_asdict[key]:
                return False
        return True
