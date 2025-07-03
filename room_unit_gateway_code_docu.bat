SET mypath=%~dp0

pyreverse -o pdf -d %mypath%\auto_generated --all-associated --all-ancestors %mypath%\room_unit_gateway\ 

pylint --disable=missing-module-docstring ^
 --disable=missing-function-docstring ^
 --disable=invalid-name ^
 --disable=line-too-long ^
 --disable=trailing-whitespace ^
 %mypath%\room_unit_gateway\