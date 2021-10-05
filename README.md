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

Authorize in storage:

```
python main.py auth -s <storage>
```

# How does it work?