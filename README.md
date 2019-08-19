# AdvancedAimingSystem: No One Lives Forever (NOLF)
Адаптированная под новые патчи версия мода **[AdvancedAimingSystem](https://github.com/GPCracker/AdvancedAimingSystem)** от **[GPCracker](https://github.com/GPCracker)**. Все необходимые файлы собраны в один **wotmod**-пакет.

## Установка (для игроков)
Извлечь файлы из архива "[AdvancedAimingSystem-NOLF.zip](./zip)" в папку **"World_of_Tanks\"**

## Сборка (для мододелов)
1. Вносим правки в скрипты **XModLib**-библиотеки в папке ["common"](./source/res/scripts/common)
2. Затем компилируем папку через **[PjOrion](https://koreanrandom.com/forum/topic/15280-)**
3. Вносим правки в скрипты **AAS**-мода в системной папке [".submodules"](./source/res/scripts/client/gui/mods/.submodules)
4. Собираем итоговый **mod_**-файл, открыв в **PjOrion** скрипт [".assembler.py"](./source/res/scripts/client/gui/mods/.submodules/.assembler.py) и запустив его через **F5**
5. Компилируем итоговый файл мода ["mod_AdvancedAimingSystem.py"](./source/res/scripts/client/gui/mods/mod_AdvancedAimingSystem.py) в **PjOrion**
6. Вписываем новую версию пакета в файле ["meta.xml"](./source/meta.xml) и собираем новый пакет, запустив **"Zip-Packer.cmd"**. (требуется наличие в системе архиватора **7-Zip**). Пакет будет сохранён в папку ["\\zip"](./zip)

В оригинальном моде присутствует система контроля версий клиента игры, которая по умолчанию отключена в конфиге ["root.xml"](./source/configs/GPCracker.AdvancedAimingSystem/root.xml), параметр **ignoreClientVersion**. Если хочется её использовать, то перед сборкой пакета следует указать поддерживаемую версию игры, это файлы ["main/header.py"](./source/res/scripts/client/gui/mods/.submodules/source/main/header.py) и ["XModLib/\_\_init\_\_.py"](./source/res/scripts/common/Lib/XModLib/__init__.py).

## История
Со списком версий и изменениями можно ознакомиться [тут](./HISTORY.md).
