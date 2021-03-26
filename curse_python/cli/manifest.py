import json
from datetime import datetime
from pathlib import Path
from typing import List
from curse_python.addons import AddonFile

class DownloadedAddon(object):
    def __init__(self, addon_id, filename, date_time):
        self.addon_id = addon_id
        self.file_name = filename
        self.file_date = datetime.fromisoformat(date_time) if isinstance(date_time, str) else date_time

class ModManifest(object):
    """
    Object for mananging a mod manifest file
    Handles serialization
    """
    def __init__(self, version_targets, wanted_addons, addon_ids_to_file_name_and_iso_format):
        afi = addon_ids_to_file_name_and_iso_format
        self.version_targets: List[str] = []
        self.wanted_addons: List[int] = []
        self.downloaded_addons: List[DownloadedAddon] = []
        for v in version_targets:
            self.version_targets.append(v)

        for a in wanted_addons:
            self.wanted_addons.append(a)

        for addon_id in addon_ids_to_file_name_and_iso_format:
            self.downloaded_addons.append(
                DownloadedAddon(int(addon_id), afi[addon_id]['file_name'], afi[addon_id]['iso_datetime'])
            )
    
    def downloaded_addon(self, addon_file: AddonFile):
        self.downloaded_addons.append(
            DownloadedAddon(
                addon_file.addon_id,
                addon_file.file_name,
                addon_file.file_date
            )
        )


    @staticmethod
    def empty():
        return ModManifest([],[],[])
    
    @staticmethod
    def fromjson(jsonstring):
        json_object = json.loads(jsonstring)
        return ModManifest(json_object["version_targets"], json_object["wanted_addons"], json_object["downloaded_addons"])
    
    def tojson(self, *args, **kwargs):
        json_object = {
            "version_targets": [],
            "wanted_addons": [],
            "downloaded_addons": {}
        }
        for v in self.version_targets:
            json_object["version_targets"].append(v)

        for a in self.wanted_addons:
            json_object["wanted_addons"].append(a)

        for f in self.downloaded_addons:
            json_object["downloaded_addons"][f.addon_id] = {
                "file_name": f.file_name,
                "iso_datetime": f.file_date.isoformat()
            }

        return json.dumps(json_object, *args, **kwargs)

    
