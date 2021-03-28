from .mods import get_mod_project, ModFile
from .exceptions import CanNotResolveException
from typing import List

def get_latest_compatible_mod_file(project_id, version_targets):
    project = get_mod_project(project_id)
    compatible_files = []
    for mod_file in project.files:
        for version_target in version_targets:
            if version_target in mod_file.game_versions:
                compatible_files.append(mod_file)
    if len(compatible_files) == 0:
        return None
    else:
        return max(compatible_files, key=lambda x: x.file_date)

def resolve_project(project_id, version_targets) -> List[ModFile]:
    project = get_latest_compatible_mod_file(project_id, version_targets)
    if not project:
        raise CanNotResolveException(project_id, version_targets)
    found = [project]
    for dependency in project.dependencies:
        found = found + resolve_project(dependency.project_id, version_targets)
    return list(dict.fromkeys(found))

def resolve_projects(project_ids, version_targets) -> List[ModFile]:
    obtained = {}
    for project_id in project_ids:
        if project_id not in obtained:
            resolved = resolve_project(project_id, version_targets)
            for resolved_dependency in resolved:
                if resolved_dependency.project_id not in obtained:
                    obtained[resolved_dependency.project_id] = resolved_dependency
    return list(obtained.values())