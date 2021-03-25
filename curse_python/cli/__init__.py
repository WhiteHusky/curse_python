from curse_python.addons import get_addon_files
from curse_python.resolving import resolve_addons
from curse_python.exceptions import CanNotResolveException
import requests
import progressbar
import argparse
import json
import sys
from os import remove
from pathlib import Path

parser = argparse.ArgumentParser(description='Download Minecraft Mods')
parser.add_argument('addon_ids', metavar='a', type=int, nargs='+', help='Addons to download')
parser.add_argument('--target', required=True, type=str, nargs='+', help='Acceptable version targets')
parser.add_argument('--save', required=True, type=str, help='Save location for mods')
parser.add_argument('--manifest', default='./mod-manifest.json', type=str, help='Manifest location for updating mods')

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

def main():
    args = parser.parse_args()
    version_targets = args.target
    addon_ids = args.addon_ids
    save_location = Path(args.save)
    manifest_location = Path(args.manifest)
    config = {}
    if manifest_location.exists():
        with open(manifest_location, 'rb') as config_file:
            config = json.load(config_file)

    print('Resolving addons...')
    addon_files = None
    try:
        addon_files = resolve_addons(addon_ids, version_targets)
    except CanNotResolveException as err:
        print(f'Addon ID {err.addon_id} is not compatiable with any versions provided.')
        sys.exit(1)
    work_done = False
    for addon_file in addon_files:
        addon_config = None
        if str(addon_file.addon_id) in config:
            addon_config = config[str(addon_file.addon_id)]
        else:
            work_done = True
            addon_config = {
                'file_name': addon_file.file_name,
                'update_epoch': 0
            }
            config[str(addon_file.addon_id)] = addon_config
        mod_path = save_location.joinpath(addon_file.file_name)
        if addon_config['update_epoch'] >= addon_file.file_date.timestamp():
            continue
        elif mod_path.exists():
            work_done = True
            remove(mod_path)

        print(f'Downloading {addon_file.file_name}')
        download_addon(save_location, addon_file)
        addon_config['update_epoch'] = addon_file.file_date.timestamp()
        addon_config['file_name'] = addon_file.file_name
    
    if work_done:
        with open(manifest_location, 'w') as config_file:
            json.dump(config, config_file)
    else:
        print('All addons up-to-date; nothing done.')
        