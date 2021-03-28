from curse_python.addons import get_addon_files
from curse_python.resolving import resolve_addons
from curse_python.exceptions import CanNotResolveException
from curse_python.cli.manifest import ModManifest, DownloadedAddon
from typing import Optional, List
import requests
import progressbar
import argparse
import json
import sys
from os import remove
from pathlib import Path

parser = argparse.ArgumentParser(description='Download CurseForge Addons')
parser.add_argument('addon_ids', metavar='a', type=int, nargs='?', help='Addons to download')
parser.add_argument('--target', type=str, nargs='+', help='Acceptable version targets')
parser.add_argument('--save', required=True, type=str, help='Save location for Addons')
parser.add_argument('--manifest', default='./addon-manifest.json', type=str, help='Manifest location for updating addons')

def download_addon(save_location, addon_file):
    r = requests.get(addon_file.download_url, stream=True)
    content_length = int(r.headers['content-length'])
    total_obtained = 0
    r.raise_for_status()
    bar = progressbar.DataTransferBar(max_value=content_length)
    with open(Path(save_location).joinpath(addon_file.file_name), 'wb') as fd:
        # Avoid downloading and finding we don't have enough space on disk.
        fd.truncate(content_length)
        fd.seek(0, 0)
        for chunk in r.iter_content(chunk_size=128):
            total_obtained = total_obtained + len(chunk)
            bar.update(total_obtained)
            fd.write(chunk)
    bar.finish()

def load_config_from_file(manifest_location):
    json_string = None
    with open(manifest_location, 'rb') as config_file:
        json_string = config_file.read()
    return ModManifest.fromjson(json_string)

    

def main():
    args = parser.parse_args()
    manifest_location = Path(args.manifest)
    mod_manifest: ModManifest = load_config_from_file(manifest_location) if manifest_location.exists() else ModManifest()
    version_targets = args.target or mod_manifest.version_targets
    wanted_addon_ids = args.addon_ids or mod_manifest.wanted_addons
    save_location = Path(args.save)
    config_update = (
        set(version_targets) != set(mod_manifest.version_targets) or
        set(wanted_addon_ids) != set(wanted_addon_ids)
    )

    print('Resolving addons...')
    addon_files = None
    try:
        addon_files = resolve_addons(wanted_addon_ids, version_targets)
    except CanNotResolveException as err:
        print(f'Addon ID {err.addon_id} is not compatiable with any versions provided.')
        sys.exit(1)
    work_done = False
    for addon_file in addon_files:
        download = False
        existing_addon: Optional[DownloadedAddon] = None
        for a in mod_manifest.downloaded_addons:
            if a.addon_id == addon_file.addon_id:
                existing_addon = a
                break
        
        if existing_addon == None:
            print(f'Will obtain new file: {addon_file.file_name}.')
            download = True
        elif existing_addon and existing_addon.file_date < addon_file.file_date:
            print(f'Will replace {existing_addon.filename} with {addon_file.filename}')
            old_addon_path = save_location.joinpath(existing_addon.file_name)
            if old_addon_path.exists():
                remove(old_addon_path)
            else:
                print(f'However it has been already removed.')
            download = True
        else:
            print(f'{addon_file.file_name} is already up to date.')
        
        if download:
            download_addon(save_location, addon_file)
            if existing_addon:
                existing_addon.file_date = addon_file.file_date
                existing_addon.file_name = addon_file.file_name
            else:
                mod_manifest.downloaded_addon(addon_file)
            work_done = True
    
    if work_done:
        ids_to_remove = []
        config_update = True
        for downloaded_addon in mod_manifest.downloaded_addons:
            found = False
            for needed_addon in addon_files:
                if downloaded_addon.addon_id == needed_addon.addon_id:
                    found = True
                    break
            
            if not found:
                print(f'Removing unneeded addon file: {downloaded_addon.file_name}')
                old_addon_path = save_location.joinpath(downloaded_addon.file_name)
                if old_addon_path.exists():
                    remove(old_addon_path)
                else:
                    print(f'However it has been already removed.')

                ids_to_remove.append(downloaded_addon.addon_id)
        
        mod_manifest.downloaded_addons = filter(lambda addon: addon.addon_id not in ids_to_remove, mod_manifest.downloaded_addons)
    else:
        print('All addons up-to-date; nothing done.')
    
    if config_update:
        with open(manifest_location, 'wb') as config_file:
            mod_manifest.version_targets = version_targets
            mod_manifest.wanted_addons = wanted_addon_ids
            config_file.write(bytes(mod_manifest.tojson(indent=4), "utf8"))
            print('Config updated.')

        