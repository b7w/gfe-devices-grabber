GFE Device Grabber
==================

[![Build Status](https://github.com/b7w/gfe-devices-grabber/actions/workflows/release.yml/badge.svg)](https://drone.b7w.me/b7w/gfe-devices-grabber)

Небольшая утилита для вытаскивания таблицы 'List Devices' из программы GFEConnector по средствам pywinauto.

Сборка
------

Установка зависимостей
```shell
poetry install
poetry run pytest
poetry build
```

Создание дистрибутива

```shell
poetry run pyinstaller src/gfe_devices_grabber/main.py --name "gfe-devices-grabber" --windowed --specpath src/ --noconfirm
```


О программе
-----------

gfe-devices-grabber - это проект с открытым исходным кодом, выпущенный по лицензии MIT.

Look, feel, be happy :-)
