# ParametersEditor
Редактор Parameters.json для настройки спавна предметов в игре SCUM
https://github.com/AndreyGladchenko/ParametersEditor/blob/main/ParametersEditor.jpg


Позволяет редактировать Parameters.json (добавлять/удалять) для настройки спавна лута.
- можно задать "разрешить/запретить" спавн лута
- можно задать повторное время появления лута для отряда, одиночки
- можно задать места появления лута (поля, леса, водоёмы)
Прибрежные (Coastal) — предметы, которые будут появляться только на морском побережье карты.
Континентальные (Continental) — предметы, которые будут появляться только на материковой части карты.
Горные (Mountain) — предметы, которые будут появляться только на горной части карты.

Необходимо запускать из папки %LocalAppData%\SCUM\Saved\Config\WindowsNoEditor\
Перед запуском необходимо извлечь (получить) Parametrs.json по умолчанию.
Для этого в игре наберите команду #ExportDefaultItemSpawningParameters
После редактирования в папке WindowsNoEditor\Items\Override будет отредактированный файл.
Переименовываете его в Parameters.json и используете в игре (на сервере)

Полная инструкция настройки спавна лута https://docs.google.com/document/d/1TIxj5OUnyrOvnXyEn3aigxLzTUQ-o-695luaaK2PTW0/edit?tab=t.0#heading=h.o4jyn6ezorng
