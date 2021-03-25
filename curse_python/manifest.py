import json
from pathlib import Path

class ModManifest(object):
    """
    Object for mananging a mod manifest file
    Handles serialization
    """
    def __init__(self, version_targets, wanted_addons, addon_file_names_and_epochs):
        self.wanted_addons = []
        file_location = Path(file_path)
        if file_location.exists():
            with open(file_location, 'rb') as config_file:
                config = json.load(config_file)
    
    def add_wanted_addon(self, addon_id):
        self.wanted_addons.append(addon_id)

    
