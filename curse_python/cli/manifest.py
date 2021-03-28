import json
from datetime import datetime
from pathlib import Path
from typing import List
from curse_python.addons import AddonFile

class DownloadedAddon(object):
    def __init__(self, addon_id, filename, date_time):
        self.addon_id: int = addon_id
        self.file_name: str = filename
        self.file_date: datetime = date_time

class ModManifest(object):
    """
    Object for mananging a mod manifest file
    Handles serialization
    """
    def __init__(self):
        self.version_targets: List[str] = []
        self.wanted_addons: List[int] = []
        self.downloaded_addons: List[DownloadedAddon] = []
    
    def downloaded_addon(self, addon_file: AddonFile):
        self.downloaded_addons.append(
            DownloadedAddon(
                addon_file.addon_id,
                addon_file.file_name,
                addon_file.file_date
            )
        )
    
    @staticmethod
    def fromjson(jsonstring):
        json_object = json.loads(jsonstring)
        mod_manifest = ModManifest()
        for version_target in json_object["version_targets"]:
            mod_manifest.version_targets.append(version_target)

        for wanted_addons in json_object["wanted_addons"]:
            mod_manifest.wanted_addons.append(int(wanted_addons))

        d = json_object["downloaded_addons"]

        for addon_id in d:
            mod_manifest.downloaded_addons.append(
                DownloadedAddon(
                    int(addon_id),
                    d[addon_id]['file_name'],
                    datetime.fromisoformat(d[addon_id]['iso_datetime'])
                )
            )
        return mod_manifest
    
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

    
