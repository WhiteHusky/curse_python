from .common import BASE_URL, get_request
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Optional
addon_cache = {}

class AddonSparse(object):
    """A sparse representation of an addon with only AddonFiles
    """
    def __init__(self, addon_id, addon_files):
        """Create a new AddonSparse object

        Args:
            addon_id (int): Addon ID
            addon_files (List[AddonFile]): Addon files
        """
        self.addon_id: int = addon_id
        self.addon_files: List[AddonFile] = addon_files
    
    def __repr__(self):
        return str(self.addon_id)

class AddonFile(object):
    """Represents a file for an addon
    """
    def __init__(self, addon_id, file_response):
        """Create a new AddonFile object

        Args:
            addon_id (int): Addon ID
            file_response (dict): Get response to populate with
        """
        self.addon_id: int = addon_id
        self.file_id: int = file_response['id']
        self.display_name: str = file_response['displayName']
        self.file_name: str = file_response['fileName']
        self.file_date: datetime = date_parser.isoparse(file_response['fileDate'])
        self.file_length: int = file_response['fileLength']
        self.release_type: int = file_response['releaseType']
        self.file_status: int = file_response['fileStatus']
        self.download_url: str = file_response['downloadUrl']
        self.alternative_id: Optional[int] = None
        if file_response['isAlternate']:
            self.alternative_id = file_response['alternateFileId']
        self.dependencies: List[AddonSparse] = []
        for dependency_response in file_response['dependencies']:
            if dependency_response['type'] == 3:
                self.dependencies.append(get_addon_files(dependency_response['addonId']))
            
        self.is_available: bool = file_response['isAvailable']
        self.modules: List[Module] = []
        for module_response in file_response['modules']:
            self.modules.append(Module(module_response))
        self.fingerprint: int = file_response['packageFingerprint']
        self.game_versions: List[str] = []
        for game_version in file_response['gameVersion']:
            self.game_versions.append(game_version)
        self.metadata: Optional[str] = file_response['installMetadata']
        self.server_pack_file_id: Optional[int] = file_response['serverPackFileId']
        self.has_install_script: bool = file_response['hasInstallScript']
        self.game_version_date_released: datetime = date_parser.isoparse(file_response['gameVersionDateReleased'])
        self.game_version_flavor: Optional[str] = file_response['gameVersionFlavor']
    
    def __repr__(self):
        return self.file_name

class Module(object):
    def __init__(self, module_response):
        self.folder_name: str = module_response['foldername']
        self.fingerprint: int = module_response['fingerprint']
    

def discard_cache() -> None:
    global addon_cache
    addon_cache = {}

def get_addon_files(addon_id, force=False) -> AddonSparse:
    """Gets a addon by it's addon ID (also known as project ID)

    Args:
        addon_id (int): Addon ID.
        force (bool, optional): Skip cache. Defaults to False.

    Returns:
        AddonSparse: A sparse addon class.
    """
    if not force and addon_id in addon_cache:
        return addon_cache[addon_id]
    else:
        file_responses = get_request(f'/addon/{addon_id}/files')
        addon_files = []
        for file_response in file_responses:
            addon_files.append(AddonFile(addon_id, file_response))
        addon = AddonSparse(addon_id, addon_files)
        addon_cache[addon_id] = addon
        return addon