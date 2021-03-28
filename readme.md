# Curse Python: A Simple CurseForge Addon Library & Manager

Given a list of addon ids (or project ids as CurseForge calls them) it will work out a list of addons and their dependencies. With the CLI interface, it can also download and manage these addons.

It's primarily targeted for Minecraft but there's nothing stopping someone using it for something else that CurseForge provides.

## CLI Use

`python -m curse_python`

```
usage: curse_python [-h] [--target TARGET [TARGET ...]] --save SAVE [--manifest MANIFEST] [addon-id [addon-id ...]]

Download CurseForge Addons

positional arguments:
  addon-id              Addons to download.

optional arguments:
  -h, --help            show this help message and exit
  --target TARGET [TARGET ...]
                        Acceptable version targets.
  --save SAVE           Save location for addons.
  --manifest MANIFEST   Manifest location for updating addons and to defer for version targets or wanted addons. Defaults to ./addon_manifest.json.
```

### Addon Manifest

```json
{
    "version_targets": [
        "1.12.2"
    ],
    "wanted_addons": [
        123456,
    ],
    "downloaded_addons": {
        "123456": {
            "file_name": "some-file-name-here.jar",
            "iso_datetime": "2019-07-23T19:19:12.153000+00:00"
        }
    }
}
```

The addon manifest keeps track of the desired version targets, wanted addons, and the files obtained. Version targets and wanted addons can be user-edited but downloaded addons are best managed by the script.

## Background

This was made primarily out of frustration that there was no light or system agnostic way to somewhat intelligently obtain Minecraft addons from CurseForge without manually searching it down and resolving dependencies.