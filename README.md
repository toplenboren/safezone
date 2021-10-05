# Savezone
CLI-utility to backup any directory to cloud

Supports:
- Yandex Disk with OAuth
- Google Drive with OAuth (DOES NOT CURRENTLY SUPPORT THIS :( )

Can:
- Backup directory or file
- Restore directory or file
- Manage cloud storage capacity

# Installation

`pip install -r requirements.txt`

# Usage

Authorize in storage:

```
python main.py auth -s <storage>
```

> Unfortunately you shoud stop the OAuth handler server manually for now. CTRL+C or CTRL+Z by default

Back up directory or file:

`python main.py backup <path> -s <yandex | google>`

```
<path>         - A path to the resource (file or directory) you want to back up to cloud

-s --storage   - Type of storage. Should be "Yandex" or "Google". Defaults to "Yandex"
-t --target    - Where to save the file. Defaults to /savezone/<file or directory name>/<current-date> 
```

List backups on cloud storage:

```
python main.py list <remote-path> -s <storage>
```

Restore directory or file:

```
python main.py restore <remote-path> -s <storage>
```

```
<path>         - A remote path to the resource. Can be obtained from main.py list. For Yandex Disk starts with 'disk:'
```

Get meta information about the storage:

```
python main.py meta -s <storage>
```

# Implementation details:

## Architecture

Project consists of different modules:

`main.py` handles CLI interface

`savezone.py` is main script that does all the work, using libraries

`cloud_storages` is library that provides access to cloud storage API

`database` is library that provides access to local KV-storage API (we use pickledb)

`oauth_handler` is library that gives access to OAuth authentitcation for certain storages

`setting, storage_registry, templates` are minor modules with helpful utils and constants for the project

