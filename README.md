# safezone
python git-like cloud-backup client

# Usage

Сохранить <directory> в сервисе с ключом <key>

`python main.py save -m <yandex | google> -k <key> <directory>`

Сохранить <directory> в сервисе, авторизоваться в процессе

`python main.py save -m yandex <directory>`  