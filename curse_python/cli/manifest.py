import json
from datetime import datetime
from pathlib import Path
from typing import List
from curse_python.mods import ModFile

class DownloadedMod(object):
    def __init__(self, project_id, filename, date_time):
        self.project_id: int = project_id
        self.file_name: str = filename
        self.file_date: datetime = date_time

class ModManifest(object):
    """
    Object for managing a mod manifest file
    Handles serialization
    """
    def __init__(self):
        self.version_targets: List[str] = []
        self.wanted_projects: List[int] = []
        self.downloaded_mods: List[DownloadedMod] = []
    
    def downloaded_mod(self, mod_file: ModFile):
        self.downloaded_mods.append(
            DownloadedMod(
                mod_file.project_id,
                mod_file.file_name,
                mod_file.file_date
            )
        )
    
    @staticmethod
    def fromjson(jsonstring):
        json_object = json.loads(jsonstring)
        mod_manifest = ModManifest()
        for version_target in json_object["version_targets"]:
            mod_manifest.version_targets.append(version_target)

        for wanted_projects in json_object["wanted_projects"]:
            mod_manifest.wanted_projects.append(int(wanted_projects))

        d = json_object["downloaded_mods"]

        for project_id in d:
            mod_manifest.downloaded_mods.append(
                DownloadedMod(
                    int(project_id),
                    d[project_id]['file_name'],
                    datetime.fromisoformat(d[project_id]['iso_datetime'])
                )
            )
        return mod_manifest
    
    def tojson(self, *args, **kwargs):
        json_object = {
            "version_targets": [],
            "wanted_projects": [],
            "downloaded_mods": {}
        }
        for v in self.version_targets:
            json_object["version_targets"].append(v)

        for a in self.wanted_projects:
            json_object["wanted_projects"].append(a)

        for f in self.downloaded_mods:
            json_object["downloaded_mods"][f.project_id] = {
                "file_name": f.file_name,
                "iso_datetime": f.file_date.isoformat()
            }

        return json.dumps(json_object, *args, **kwargs)

    
