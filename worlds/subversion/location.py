from typing import Optional

from BaseClasses import Location, Region
from .config import base_id, is_apworld, open_file_apworld_compatible

from subversion_rando.location_data import Location as SvLocation, pullCSV

if is_apworld():
    # not using os.path.join because this is a path inside the zip file, that wants /
    csv_file = open_file_apworld_compatible("/".join(["subversion", "subversion_rando", "subversiondata12.csv"]))
    location_data = pullCSV(csv_file)
else:
    location_data = pullCSV()

id_to_name = {
    loc["plmparamlo"] + base_id: loc_name
    for loc_name, loc in location_data.items()
}

name_to_id = {
    n: id_
    for id_, n in id_to_name.items()
}

fallen_locs = {
    loc["alternateplmparamlo"]: loc["plmparamlo"]
    for loc in location_data.values()
    if loc["alternateplmparamlo"]
}
"""
fallen location id from rom (that AP doesn't know)
to location id that AP knows about
"""


class SubversionLocation(Location):
    game = "Subversion"
    sv_loc: SvLocation

    def __init__(self,
                 player: int,
                 name: str,
                 parent: Optional[Region] = None) -> None:
        loc_id = name_to_id[name]
        super().__init__(player, name, loc_id, parent)
        self.sv_loc = location_data[name]
