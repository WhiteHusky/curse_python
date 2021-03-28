from curse_python.mods import get_mod_project, ModFile
from curse_python.resolving import resolve_projects
from curse_python.exceptions import CanNotResolveException
from curse_python.cli.manifest import ModManifest, DownloadedMod
from typing import Optional, List
import requests
import progressbar
import argparse
import json
import sys
from os import remove
from pathlib import Path

parser = argparse.ArgumentParser(
    prog='curse_python',
    description='Download CurseForge Project Mod Files'
)
parser.add_argument('project_ids', metavar='project-id', type=int, nargs='*', help='Project IDs to obtain mod files from.')
parser.add_argument('--target', type=str, nargs='+', help='Acceptable version targets.')
parser.add_argument('--save', required=True, type=str, help='Save location for mods.')
parser.add_argument('--manifest', default='./mod-manifest.json', type=str, help='Manifest location for updating mods and to defer for version targets or wanted project ids. Defaults to ./mod-manifest.json.')

def download_mod_files(save_location, mod_files: List[ModFile]):
    session = requests.Session()
    total = 0
    total_obtained = 0
    for mod_file in mod_files:
        total += mod_file.file_length
    widgets = [
        progressbar.widgets.Percentage(),
        ' of ', progressbar.DataSize('max_value'),
        ' @ ', progressbar.AdaptiveTransferSpeed(),
        ', ', progressbar.Variable('file'),
        ' ', progressbar.Bar(),
        ' ', progressbar.Timer(),
        ' ', progressbar.AdaptiveETA()
    ]

    with progressbar.ProgressBar(max_value=total, widgets=widgets).start() as bar:
        for mod_file in mod_files:
            bar.update(total_obtained, file=mod_file.file_name)
            r = session.get(mod_file.download_url, stream=True)
            #content_length = int(r.headers['content-length'])
            r.raise_for_status()
            with open(Path(save_location).joinpath(mod_file.file_name), 'wb') as fd:
                # Avoid downloading and finding we don't have enough space on disk.
                fd.truncate(mod_file.file_length)
                fd.seek(0, 0)
                for chunk in r.iter_content(chunk_size=128):
                    total_obtained = total_obtained + len(chunk)
                    bar.update(total_obtained)
                    fd.write(chunk)

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
    wanted_project_ids = args.project_ids or mod_manifest.wanted_projects
    save_location = Path(args.save)
    config_update = (
        set(version_targets) != set(mod_manifest.version_targets) or
        set(wanted_project_ids) != set(wanted_project_ids)
    )

    print('Resolving Projects...')
    mod_files = None
    try:
        mod_files = resolve_projects(wanted_project_ids, version_targets)
    except CanNotResolveException as err:
        print(f'Project ID {err.project_id} is not compatible with any versions provided.')
        sys.exit(1)
    work_done = False
    to_download: List[ModFile] = []
    for mod_file in mod_files:
        download = False
        existing_mod: Optional[DownloadedMod] = None
        for downloaded_mod in mod_manifest.downloaded_mods:
            if downloaded_mod.project_id == mod_file.project_id:
                existing_mod = downloaded_mod
                break
        
        if existing_mod == None:
            print(f'Will obtain new file: {mod_file.file_name}.')
            download = True
        elif existing_mod and existing_mod.file_date < mod_file.file_date:
            print(f'Will replace {existing_mod.file_name} with {mod_file.file_name}')
            old_mod_path = save_location.joinpath(existing_mod.file_name)
            if old_mod_path.exists():
                remove(old_mod_path)
            else:
                print(f'However it has been already removed.')
            download = True
        else:
            print(f'{mod_file.file_name} is already up to date.')
        
        if download:
            to_download.append(mod_file)
            if existing_mod:
                existing_mod.file_date = mod_file.file_date
                existing_mod.file_name = mod_file.file_name
            else:
                mod_manifest.downloaded_mod(mod_file)
            work_done = True
    
    if len(to_download) > 0:
        download_mod_files(save_location, to_download)

    if work_done:
        project_ids_to_remove = []
        config_update = True
        for downloaded_mods in mod_manifest.downloaded_mods:
            found = False
            for needed_mod in mod_files:
                if downloaded_mods.project_id == needed_mod.project_id:
                    found = True
                    break
            
            if not found:
                print(f'Removing unneeded mod file: {downloaded_mods.file_name}')
                old_mod_path = save_location.joinpath(downloaded_mods.file_name)
                if old_mod_path.exists():
                    remove(old_mod_path)
                else:
                    print(f'However it has been already removed.')

                project_ids_to_remove.append(downloaded_mods.project_id)
        
        mod_manifest.downloaded_mods = filter(lambda mod_file: mod_file.project_id not in project_ids_to_remove, mod_manifest.downloaded_mods)
    else:
        print('All mods up-to-date; nothing done.')
    
    if config_update:
        with open(manifest_location, 'wb') as config_file:
            mod_manifest.version_targets = version_targets
            mod_manifest.wanted_projects = wanted_project_ids
            config_file.write(bytes(mod_manifest.tojson(indent=4), "utf8"))
            print('Config updated.')

        