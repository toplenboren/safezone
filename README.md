# Savezone
CLI-utility to backup any directory to cloud

Supports:
- Yandex Disk with OAuth
- Google Drive with OAuth

Can:
- Backup directory or file
- Restore directory or files
- Manage cloud storage capacity - remove old files

# Installation

`pip install -r requirements.txt`

# Usage

Back up directory or file:

`python main.py backup <path> -s <yandex | google> -t <path> -p`

```
-s --storage   - Type of storage. Should be "Yandex" or "Google". Defaults to "Yandex"
-t --target    - Where to save the file. Defaults to /savezone/<file or directory name>/<current-date>
-o --owerwrite - When saving – owerwrite the last version of this backup
```

Restore directory or file:

```
python main.py restore <name> -s <storage> -t <target>
```

Get meta information about the storage:

```
python main.py meta -s <storage>
```






Сохранить <directory> в сервисе с ключом <key>

`python main.py save -m <yandex | google> -k <key> <directory>`

Сохранить <directory> в сервисе, авторизоваться в процессе

Эта операция добавит новое хранилище

`python main.py save -m yandex <directory>`  

Посмотреть список добавленых хранилищ

`python main.py storages`

Добавить новое хранилище <name>

`python main.py add -m <method> -n <name>`

Посмотреть список файлов:

`python main.py ls -m <method> <directory>`

Посмотреть мета-информацию о хранилище:
`python main.py meta -s <storage>`

# How does it work?