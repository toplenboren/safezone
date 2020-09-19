# Savezone
python git-like cloud-backup client

# Usage

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