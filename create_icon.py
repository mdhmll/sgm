import base64
import os

# Данные иконки в формате base64
icon_data = """
AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAMMOAADDDgAAAAAAAAAA
AAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////ANK6niTRuZ2s0bmd7NG5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5ne3RuZ2s0rqeJP///wD///8A////AP//
/wD///8A////AP///wD///8A////ANK5nX/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/SuZ1/////AP//
/wD///8A////AP///wD///8A////ANK6nibRuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9K6
nibRuZ0E0bmdCP///wD///8A////AP///wDRuZ2s0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ2s0bmdotG5ncH///8A////AP///wD///8A0bmd7NG5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd7NG5nf/RuZ3/0bmdCP///wD///8A////ANK5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nX////8A////AP///wDRuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/////AP///wD///8A0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/////wD///8A////ANK5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf////8A////AP///wDRuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/////AP///wD///8A0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/////wD///8A////ANK5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf////8A////AP//
/wDRuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/////AP//
/wD///8A0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd////
/wD///8A////ANK5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf////8A////AP///wDRuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/////AP///wD///8A0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/////wD///8A////ANK5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5nf/SuZ3/0rmd/9K5
nf/SuZ3/0rmd/9K5nf////8A////AP///wDRuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/////AP///wD///8A0bmd7NG5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd7P///wD///8A////ANO6nq/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9O6nq////8A////AP///wDSvJ4n0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/SvJ4n////AP///wD///8A////ANW2qhHRuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/1baqEf///wD///8A////AP///wD///8A////ANG5
nZ3RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmdnf///wD///8A////AP///wD///8A////AP//
/wD///8A0rqeI9G5ndLRuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5
nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd/9G5nf/RuZ3/0bmd0tK6niP///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8AzcyZBdO5nkDRuZ2E0bmdnNG5nZ3RuZ2d0bmdndG5nZ3RuZ2d0bmdndG5
nZ3RuZ2d0bmdndG5nZ3RuZ2d0bmdndG5nZ3RuZ2E07mfQM3MmQX///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//
/wD///8A////AP///wD///8A////AP//AAP//wAD//8AAP/+AAB//AAAP/gAAB/wAAAP4AAAB8AAAAPA
AAADgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAHA
AAADwAAAA/AAAA/4AAAf/AAAP/4AAH//AAD//wAD//8AA/8=
"""

# Путь для сохранения файла иконки
icon_path = os.path.join(os.path.dirname(__file__), "school_icon.ico")

# Запись данных иконки в файл
with open(icon_path, "wb") as icon_file:
    icon_file.write(base64.b64decode(icon_data))

print(f"Иконка успешно создана по пути: {icon_path}")
