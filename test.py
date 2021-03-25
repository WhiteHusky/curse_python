from curse_python.addons import get_addon_files
from curse_python.resolving import resolve_addons
import threading
import requests
import progressbar
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='Download Minecraft Mods')
parser.add_argument('addon_ids', metavar='a', type=int, nargs='+', help='Addons to download')
parser.add_argument('--target', required=True, type=str, nargs='+', help='Acceptable version targets')
parser.add_argument('--save', required=True, type=str, help='Save location for mods')

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

version_targets_x = ['1.12.2']
addon_ids_x = [
    223794,
    228027,
    238222,
    270789,
    227443,
    69163,
    291737,
    271835,
]
args = parser.parse_args()
version_targets = args.target
print('Resolving addons...')
addon_files = resolve_addons(args.addon_ids, version_targets)
for addon_file in addon_files:
    print(f'Downloading {addon_file.file_name}')
    download_addon(args.save, addon_file)