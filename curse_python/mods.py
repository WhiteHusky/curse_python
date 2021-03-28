from .common import get_request
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Optional
project_cache = {}

class ModProject(object):
    """A mod project containing a list of mod files available.
    """
    def __init__(self, project_id):
        """Create a new ModProject object

        Args:
            project_id (int): Project ID
        """
        self.project_id: int = project_id
        self.files: List[ModFile] = []
    
    def __repr__(self):
        return str(self.project_id)

class ModFile(object):
    """Represents a file for a mod project
    """
    def __init__(self, project_id, file_response):
        """Create a new ModFile object

        Args:
            project_id (int): Project ID
            file_response (dict): Get response to populate with
        """
        self.project_id: int = project_id
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
        self.dependencies: List[ModProject] = []
        for dependency_response in file_response['dependencies']:
            if dependency_response['type'] == 3:
                self.dependencies.append(get_mod_project(dependency_response['addonId']))

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
    global project_cache
    project_cache = {}

def get_mod_project(project_id, force=False) -> ModProject:
    """Gets a project by it's project ID

    Args:
        project_id (int): Project ID.
        force (bool, optional): Skip cache. Defaults to False.

    Returns:
        ModProject: A ModProject class containing its files.
    """
    if not force and project_id in project_cache:
        return project_cache[project_id]
    else:
        file_responses = get_request(f'/addon/{project_id}/files')
        project = ModProject(project_id)
        for file_response in file_responses:
            project.files.append(ModFile(project_id, file_response))

        project_cache[project_id] = project
        return project
