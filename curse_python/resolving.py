from .addons import get_addon_files, AddonFile
from .exceptions import CanNotResolveException
from typing import List

def get_latest_addon_file(addon_id, version_targets):
    addon = get_addon_files(addon_id)
    compatible_files = []
    for addon_file in addon.addon_files:
        for version_target in version_targets:
            if version_target in addon_file.game_versions:
                compatible_files.append(addon_file)
    if len(compatible_files) == 0:
        return None
    else:
        return max(compatible_files, key=lambda x: x.file_date)

def resolve_addon(addon_id, version_targets) -> List[AddonFile]:
    addon = get_latest_addon_file(addon_id, version_targets)
    if not addon:
        raise CanNotResolveException(addon_id, version_targets)
    found = [addon]
    for dependency in addon.dependencies:
        found = found + resolve_addon(dependency.addon_id, version_targets)
    return list(dict.fromkeys(found))

def resolve_addons(addon_ids, version_targets) -> List[AddonFile]:
    obtained = {}
    for addon_id in addon_ids:
        if addon_id not in obtained:
            resolved = resolve_addon(addon_id, version_targets)
            for resolved_dependency in resolved:
                if resolved_dependency.addon_id not in obtained:
                    obtained[resolved_dependency.addon_id] = resolved_dependency
    return list(obtained.values())